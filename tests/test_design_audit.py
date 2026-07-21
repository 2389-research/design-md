# ABOUTME: Tests for design_audit.py, the Stop hook that requests a design
# ABOUTME: conformance audit after turns that modified files.
import json
import subprocess
import sys
from pathlib import Path

import design_audit

SCRIPT = Path(__file__).parent.parent / "hooks" / "scripts" / "design_audit.py"


def make_transcript(tmp_path, entries):
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in entries))
    return p


def user_msg(text):
    return {"type": "user", "message": {"content": [{"type": "text", "text": text}]}}


def tool_result_msg():
    return {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}}


def assistant_tool_use(name):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": {}}]}}


def test_detects_write_tool_in_last_turn(tmp_path):
    t = make_transcript(tmp_path, [
        user_msg("hi"),
        assistant_tool_use("Read"),
        user_msg("change the button"),
        assistant_tool_use("Edit"),
        tool_result_msg(),
    ])
    assert design_audit.turn_modified_files(t) is True


def test_ignores_writes_from_earlier_turns(tmp_path):
    t = make_transcript(tmp_path, [
        user_msg("build it"),
        assistant_tool_use("Write"),
        tool_result_msg(),
        user_msg("thanks, what does it do?"),
        assistant_tool_use("Read"),
    ])
    assert design_audit.turn_modified_files(t) is False


def test_tool_results_are_not_turn_boundaries(tmp_path):
    t = make_transcript(tmp_path, [
        user_msg("change the button"),
        assistant_tool_use("Edit"),
        tool_result_msg(),
        assistant_tool_use("Bash"),
    ])
    assert design_audit.turn_modified_files(t) is True


def test_false_for_missing_transcript(tmp_path):
    assert design_audit.turn_modified_files(tmp_path / "nope.jsonl") is False


def test_skips_malformed_lines(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text("garbage\n" + json.dumps(user_msg("x")) + "\n" + json.dumps(assistant_tool_use("Edit")))
    assert design_audit.turn_modified_files(p) is True


def run_hook(payload):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_blocks_with_audit_prompt(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Edit")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": False})
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["decision"] == "block"
    assert "DESIGN.md" in out["reason"]


def test_silent_when_stop_hook_active(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Edit")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": True})
    assert result.stdout.strip() == ""


def test_silent_when_no_design_md(tmp_path):
    (tmp_path / ".git").mkdir()
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Edit")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": False})
    assert result.stdout.strip() == ""


def test_silent_when_turn_wrote_nothing(tmp_path):
    (tmp_path / "DESIGN.md").write_text("# design")
    t = make_transcript(tmp_path, [user_msg("x"), assistant_tool_use("Read")])
    result = run_hook({"cwd": str(tmp_path), "transcript_path": str(t), "stop_hook_active": False})
    assert result.stdout.strip() == ""
