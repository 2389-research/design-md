#!/usr/bin/env python3
# ABOUTME: Pre-hook for SessionStart and UserPromptSubmit: if the project has a
# ABOUTME: DESIGN.md, inject a pointer to using-design; if not, inject a small
# ABOUTME: conditional note letting the main model judge whether to offer design-md.
import hashlib
import json
import os
import sys
import time
from pathlib import Path

POINTER = (
    "This project has a design system file: {path}. Before any work that "
    "changes user-visible output (UI, styling, terminal output, user-facing "
    "copy), invoke the using-design skill and conform to DESIGN.md."
)

CREATION_HINT = (
    "Note (applies to this entire session, remember it): this project has "
    "no DESIGN.md. If the current request — or ANY later request in this "
    "session — involves visual/UI/design work, offer once to capture design "
    "intent as an enforceable DESIGN.md via the design-md skill. Whether the "
    "user accepts or declines, silence this note permanently by running: "
    "mkdir -p {marker_dir} && touch {marker}. For non-design requests, do "
    "not mention this note or touch the marker, but keep it in mind for "
    "later design requests."
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


def hint_marker(project_root: Path) -> Path:
    state_home = Path(
        os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
    )
    digest = hashlib.sha256(str(project_root).encode()).hexdigest()[:16]
    return state_home / "design-md" / "offered" / digest


def session_marker(session_id: str) -> Path:
    state_home = Path(
        os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
    )
    return state_home / "design-md" / "seen" / session_id


def prune_stale_session_markers(seen_dir: Path, max_age_days: int = 7) -> None:
    cutoff = time.time() - max_age_days * 24 * 3600
    for entry in seen_dir.iterdir():
        if entry.is_file() and entry.stat().st_mtime < cutoff:
            entry.unlink(missing_ok=True)


def maybe_creation_hint(cwd: Path, prompt: str, session_id: str) -> str | None:
    if not prompt:
        return None
    marker = hint_marker(find_project_root(cwd))
    if marker.exists():
        return None
    if session_id:
        seen = session_marker(session_id)
        if seen.exists():
            return None
        seen.parent.mkdir(parents=True, exist_ok=True)
        seen.touch()
        prune_stale_session_markers(seen.parent)
    return CREATION_HINT.format(marker_dir=marker.parent, marker=marker)


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
    hint = maybe_creation_hint(
        cwd, data.get("prompt") or "", data.get("session_id") or ""
    )
    if hint:
        print(hint)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
