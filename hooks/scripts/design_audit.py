#!/usr/bin/env python3
# ABOUTME: Stop hook: after a turn that modified files in a project with a
# ABOUTME: DESIGN.md, block once and request a conformance audit against it.
import json
import sys
from pathlib import Path

from design_context import find_design_md

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}

AUDIT_PROMPT = (
    "Design audit: this turn modified files and the project has a design "
    "system file ({path}). If any change affects user-visible output (UI, "
    "styling, terminal output, user-facing copy), review it against DESIGN.md "
    "like a code review: report conformance and divergences, then fix "
    "divergences or explicitly flag them with reasoning. If nothing "
    "user-visible changed, state that no design audit is needed and stop."
)


def _is_tool_result(entry: dict) -> bool:
    content = entry.get("message", {}).get("content")
    if isinstance(content, list):
        return any(
            isinstance(b, dict) and b.get("type") == "tool_result" for b in content
        )
    return False


def turn_modified_files(transcript_path: Path) -> bool:
    if not Path(transcript_path).is_file():
        return False
    entries = []
    for line in Path(transcript_path).read_text().splitlines():
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    last_user = -1
    for i, entry in enumerate(entries):
        if (
            entry.get("type") == "user"
            and not entry.get("isSidechain")
            and not _is_tool_result(entry)
        ):
            last_user = i
    for entry in entries[last_user + 1 :]:
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content") or []
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") in WRITE_TOOLS
            ):
                return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if data.get("stop_hook_active"):
        return
    cwd = Path(data.get("cwd") or Path.cwd())
    design = find_design_md(cwd)
    if design is None:
        return
    if not turn_modified_files(Path(data.get("transcript_path", ""))):
        return
    print(json.dumps({"decision": "block", "reason": AUDIT_PROMPT.format(path=design)}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
