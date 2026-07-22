#!/usr/bin/env python3
# ABOUTME: Pre-hook for SessionStart and UserPromptSubmit: if the project has a
# ABOUTME: DESIGN.md, inject a pointer to using-design; if not and the prompt is
# ABOUTME: design-ish, hint once (per project, ever) that design-md can create one.
import hashlib
import json
import os
import re
import sys
from pathlib import Path

POINTER = (
    "This project has a design system file: {path}. Before any work that "
    "changes user-visible output (UI, styling, terminal output, user-facing "
    "copy), invoke the using-design skill and conform to DESIGN.md."
)

CREATION_HINT = (
    "This project has no DESIGN.md. The current request looks like visual/UI "
    "design work — offer once to capture design intent as an enforceable "
    "DESIGN.md via the design-md skill. If the user declines, drop it; this "
    "hint will not repeat."
)

DESIGN_ISH = re.compile(
    r"\b(re)?design(ed|ing)?\b"
    r"|\bre?styl(e|ing|ed)\b|\bstylesheet\b|\bcss\b"
    r"|\btheme\b|\btypography\b|\bfonts?\b"
    r"|\bcolou?r( scheme| palette)?s?\b|\bpalette\b"
    r"|\blayout\b|\bux\b|\bui\b|\bvisual(ly)?\b|\bbranding\b"
    r"|\blook[- ]and[- ]feel\b|\blanding page\b",
    re.IGNORECASE,
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


def find_project_root(start: Path) -> Path:
    current = Path(start).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return current


def is_design_ish(prompt: str) -> bool:
    return bool(DESIGN_ISH.search(prompt))


def hint_marker(project_root: Path) -> Path:
    state_home = Path(
        os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
    )
    digest = hashlib.sha256(str(project_root).encode()).hexdigest()[:16]
    return state_home / "design-md" / "offered" / digest


def maybe_creation_hint(cwd: Path, prompt: str) -> str | None:
    if not prompt or not is_design_ish(prompt):
        return None
    marker = hint_marker(find_project_root(cwd))
    if marker.exists():
        return None
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    return CREATION_HINT


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    cwd = Path(data.get("cwd") or Path.cwd())
    design = find_design_md(cwd)
    if design is not None:
        print(POINTER.format(path=design))
        return
    hint = maybe_creation_hint(cwd, data.get("prompt") or "")
    if hint:
        print(hint)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
