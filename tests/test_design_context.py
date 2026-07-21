# ABOUTME: Tests for design_context.py, the SessionStart/UserPromptSubmit hook
# ABOUTME: that injects a pointer when the project contains a DESIGN.md.
import json
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
