#!/usr/bin/env python3
# ABOUTME: Pre-hook for SessionStart and UserPromptSubmit: if the project has a
# ABOUTME: DESIGN.md, inject a one-line pointer to invoke the using-design skill.
import json
import sys
from pathlib import Path

POINTER = (
    "This project has a design system file: {path}. Before any work that "
    "changes user-visible output (UI, styling, terminal output, user-facing "
    "copy), invoke the using-design skill and conform to DESIGN.md."
)


def find_design_md(start: Path) -> Path | None:
    current = Path(start).resolve()
    for candidate in [current, *current.parents]:
        design = candidate / "DESIGN.md"
        if design.is_file():
            return design
        if (candidate / ".git").exists():
            return None
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    cwd = Path(data.get("cwd") or Path.cwd())
    design = find_design_md(cwd)
    if design is None:
        return
    print(POINTER.format(path=design))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
