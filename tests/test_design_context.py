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


def run_hook_with_state(payload, state_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "XDG_STATE_HOME": str(state_dir)},
    )


def test_design_ish_prompt_detection():
    assert design_context.is_design_ish("make the landing page pop with a new color palette")
    assert design_context.is_design_ish("restyle the nav CSS")
    assert design_context.is_design_ish("pick a typography scale")
    assert not design_context.is_design_ish("fix the failing database migration")
    assert not design_context.is_design_ish("rename the parser module")


def test_hints_creation_once_for_design_ish_prompt(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    payload = {"cwd": str(repo), "prompt": "redesign the settings page layout"}

    first = run_hook_with_state(payload, state)
    assert first.returncode == 0
    assert "design-md" in first.stdout
    assert "DESIGN.md" in first.stdout

    second = run_hook_with_state(payload, state)
    assert second.returncode == 0
    assert second.stdout.strip() == ""


def test_no_hint_for_non_design_prompt(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo), "prompt": "fix the CI pipeline"}, state)
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
    for name in ("repo-a", "repo-b"):
        repo = tmp_path / name
        repo.mkdir()
        (repo / ".git").mkdir()
        result = run_hook_with_state(
            {"cwd": str(repo), "prompt": "new color scheme for the dashboard"}, state
        )
        assert "design-md" in result.stdout, f"hint missing for fresh project {name}"
