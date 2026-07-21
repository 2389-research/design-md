# 03 — Revision ripple

## Setup
Project with DESIGN.md whose components reference {colors.primary}.

## Prompt
"Actually I think the primary color should be a warm orange instead."

## Pass criteria
- [ ] design-md skill revision flow: current vs proposed rendered side
      by side BEFORE any file change
- [ ] Ripple effects surfaced (components referencing colors.primary,
      Colors prose, contrast with on-primary)
- [ ] Existing rationale updated, not deleted; new reaction recorded
- [ ] validate_design.py re-run after the write

## Fail modes to watch
- Token silently rewritten with no rendering
- on-primary left unreadable against the new orange with no mention
