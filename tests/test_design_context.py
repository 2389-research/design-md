# ABOUTME: Tests for design_context.py, the SessionStart/UserPromptSubmit hook
# ABOUTME: that injects a pointer when the project contains a DESIGN.md.
import json
import os
import subprocess
import sys
from pathlib import Path

import design_context

SCRIPT = Path(__file__).parent.parent / "hooks" / "scripts" / "design_context.py"


def test_finds_design_md_in_cwd(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    assert design_context.find_design_md(tmp_path) == tmp_path / "DESIGN.md"


def test_finds_design_md_walking_up_to_git_root(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "DESIGN.md").write_text("# design")
    sub = tmp_path / "src" / "components"
    sub.mkdir(parents=True)
    assert design_context.find_design_md(sub) == tmp_path / "DESIGN.md"


def test_stops_at_git_root(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")  # outside the repo
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    assert design_context.find_design_md(repo) is None


def test_none_when_absent(tmp_path):
    (tmp_path / ".git").mkdir()
    assert design_context.find_design_md(tmp_path) is None


def run_hook(payload):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_emits_pointer_when_design_md_exists(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    result = run_hook({"cwd": str(tmp_path)})
    assert result.returncode == 0
    assert "DESIGN.md" in result.stdout
    assert "using-design" in result.stdout


def test_silent_when_no_design_md(tmp_path):
    (tmp_path / ".git").mkdir()
    result = run_hook({"cwd": str(tmp_path)})
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_silent_on_malformed_stdin(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], input="not json", capture_output=True, text=True
    )
    assert result.returncode == 0


def test_silent_on_empty_payload(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], input="{}", capture_output=True, text=True
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


# --- creation-offer hint (no DESIGN.md present) ---
# The hook does not judge whether the prompt is design work — that judgment
# belongs to the main model, which reads the injected note. The hook only
# gates on: DESIGN.md absent, prompt present, marker absent.


def run_hook_with_state(payload, state_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "XDG_STATE_HOME": str(state_dir)},
    )


def test_hint_emitted_on_any_prompt_when_no_design_md(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo), "prompt": "fix the CI pipeline"}, state)
    assert result.returncode == 0
    assert "design-md" in result.stdout
    assert "DESIGN.md" in result.stdout


def test_hint_names_the_marker_path(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo), "prompt": "hello"}, state)
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    marker = design_context.hint_marker(repo)
    assert str(marker) in result.stdout


def test_hint_does_not_touch_marker_itself(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    payload = {"cwd": str(repo), "prompt": "hello"}
    first = run_hook_with_state(payload, state)
    second = run_hook_with_state(payload, state)
    assert "design-md" in first.stdout
    assert "design-md" in second.stdout  # repeats until the model silences it


def test_hint_silenced_by_marker(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    marker = design_context.hint_marker(repo)
    # hint_marker honors XDG_STATE_HOME from *this* process env, so compute
    # the marker the way the subprocess will see it.
    result_env_marker = state / "design-md" / "offered" / marker.name
    result_env_marker.parent.mkdir(parents=True)
    result_env_marker.touch()
    result = run_hook_with_state({"cwd": str(repo), "prompt": "hello"}, state)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_no_hint_without_prompt_field(tmp_path):
    # SessionStart payloads carry no prompt — hint must stay silent there.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo)}, state)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_pointer_takes_precedence_over_hint(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "DESIGN.md").write_text("# design")
    state = tmp_path / "state"
    result = run_hook_with_state(
        {"cwd": str(repo), "prompt": "restyle the nav CSS"}, state
    )
    assert "using-design" in result.stdout
    assert "offer" not in result.stdout.lower()


def test_hint_marker_is_per_project(tmp_path):
    state = tmp_path / "state"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    for repo in (repo_a, repo_b):
        repo.mkdir()
        (repo / ".git").mkdir()
    marker_a = design_context.hint_marker(repo_a)
    marker_b = design_context.hint_marker(repo_b)
    assert marker_a != marker_b
    # silencing repo-a leaves repo-b's hint live
    silenced = state / "design-md" / "offered" / marker_a.name
    silenced.parent.mkdir(parents=True)
    silenced.touch()
    result_a = run_hook_with_state({"cwd": str(repo_a), "prompt": "hi"}, state)
    result_b = run_hook_with_state({"cwd": str(repo_b), "prompt": "hi"}, state)
    assert result_a.stdout.strip() == ""
    assert "design-md" in result_b.stdout
