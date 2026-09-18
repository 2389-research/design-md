# ABOUTME: Tests for design_offer.py, the UserPromptSubmit hook that offers
# ABOUTME: DESIGN.md creation once per project when the project has none.
import json
import os
import subprocess
import sys
from pathlib import Path

import design_offer

SCRIPT = Path(__file__).parent.parent / "hooks" / "scripts" / "design_offer.py"


def run_hook_with_state(payload, state_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "XDG_STATE_HOME": str(state_dir)},
    )


def make_repo(tmp_path, name="repo"):
    repo = tmp_path / name
    repo.mkdir()
    (repo / ".git").mkdir()
    return repo


# --- the hook is silent whenever a DESIGN.md already exists ---
# Adherence is not the hook's job: an agent finds and reads an existing
# DESIGN.md on its own. The hook only covers the case it cannot discover —
# a design system that does not exist yet.


def test_silent_when_design_md_exists_in_cwd(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "DESIGN.md").write_text("# design")
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo), "prompt": "restyle the nav"}, state)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_silent_when_design_md_exists_up_the_tree(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "DESIGN.md").write_text("# design")
    sub = repo / "src" / "components"
    sub.mkdir(parents=True)
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(sub), "prompt": "restyle the nav"}, state)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_design_md_outside_the_repo_does_not_silence_the_offer(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# not this project's")
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo), "prompt": "hello"}, state)
    assert "design-md" in result.stdout


# --- failure modes stay silent and exit 0 ---


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


def test_no_offer_without_prompt_field(tmp_path):
    # SessionStart payloads carry no prompt — the offer must stay silent there.
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo)}, state)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


# --- the creation offer ---
# The hook does not judge whether the prompt is design work — that judgment
# belongs to the main model, which reads the injected note. The hook only
# gates on: DESIGN.md absent, prompt present, marker absent.


def test_offer_emitted_on_any_prompt_when_no_design_md(tmp_path):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    result = run_hook_with_state(
        {"cwd": str(repo), "prompt": "fix the CI pipeline"}, state
    )
    assert result.returncode == 0
    assert "design-md" in result.stdout
    assert "DESIGN.md" in result.stdout


def test_offer_names_the_marker_path(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    result = run_hook_with_state({"cwd": str(repo), "prompt": "hello"}, state)
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    assert str(design_offer.offer_marker(repo)) in result.stdout


def test_hook_does_not_touch_permanent_marker_itself(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    # different sessions: the offer repeats until the model silences it
    first = run_hook_with_state(
        {"cwd": str(repo), "prompt": "hello", "session_id": "s1"}, state
    )
    second = run_hook_with_state(
        {"cwd": str(repo), "prompt": "hello", "session_id": "s2"}, state
    )
    assert "design-md" in first.stdout
    assert "design-md" in second.stdout
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    assert not design_offer.offer_marker(repo).exists()


def test_offer_once_per_session(tmp_path):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    payload = {"cwd": str(repo), "prompt": "hello", "session_id": "same-session"}
    first = run_hook_with_state(payload, state)
    second = run_hook_with_state(payload, state)
    assert "design-md" in first.stdout
    assert second.stdout.strip() == ""


def test_offer_emitted_every_time_without_session_id(tmp_path):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    payload = {"cwd": str(repo), "prompt": "hello"}
    first = run_hook_with_state(payload, state)
    second = run_hook_with_state(payload, state)
    assert "design-md" in first.stdout
    assert "design-md" in second.stdout


def test_offer_silenced_by_marker(tmp_path):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    # offer_marker honors XDG_STATE_HOME from *this* process env, so compute
    # the marker the way the subprocess will see it.
    marker = state / "design-md" / "offered" / design_offer.offer_marker(repo).name
    marker.parent.mkdir(parents=True)
    marker.touch()
    result = run_hook_with_state({"cwd": str(repo), "prompt": "hello"}, state)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_offer_marker_is_per_project(tmp_path):
    state = tmp_path / "state"
    repo_a = make_repo(tmp_path, "repo-a")
    repo_b = make_repo(tmp_path, "repo-b")
    marker_a = design_offer.offer_marker(repo_a)
    assert marker_a != design_offer.offer_marker(repo_b)
    # silencing repo-a leaves repo-b's offer live
    silenced = state / "design-md" / "offered" / marker_a.name
    silenced.parent.mkdir(parents=True)
    silenced.touch()
    result_a = run_hook_with_state({"cwd": str(repo_a), "prompt": "hi"}, state)
    result_b = run_hook_with_state({"cwd": str(repo_b), "prompt": "hi"}, state)
    assert result_a.stdout.strip() == ""
    assert "design-md" in result_b.stdout


def test_stale_session_markers_are_pruned(tmp_path):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    seen_dir = state / "design-md" / "seen"
    seen_dir.mkdir(parents=True)
    stale = seen_dir / "old-session"
    stale.touch()
    week_plus = 8 * 24 * 3600
    os.utime(stale, (os.path.getmtime(stale) - week_plus,) * 2)
    fresh = seen_dir / "fresh-session"
    fresh.touch()
    run_hook_with_state({"cwd": str(repo), "prompt": "hi", "session_id": "s9"}, state)
    assert not stale.exists()
    assert fresh.exists()
