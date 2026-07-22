<!-- ABOUTME: Eval scenario — revising colors.primary in an existing DESIGN.md must surface ripple effects before any write. -->
<!-- ABOUTME: Pass = side-by-side render, referencing components and contrast flagged, rationale preserved; fail = silent token rewrite. -->

# 03 — Revision ripple

## Setup
Throwaway project with a committed DESIGN.md. To build it, copy the
plugin's `templates/DESIGN.template.md` into the throwaway project as
`DESIGN.md`, replace `PROJECT_NAME` with a real name (e.g.
`ripple-demo`), and set `colors.primary` to `#2563EB` (leave
`colors.on-primary` at `#ffffff`).

Note the template's `components.button-primary` sets `backgroundColor`
to `{colors.primary}` and `textColor` to `{colors.on-primary}` — so a
primary-color change must surface that component ripple and the
on-primary contrast question.

## Prompt
"Actually I think the primary color should be a warm orange instead."

## Pass criteria
- [ ] design-md skill revision flow: current vs proposed rendered side
      by side BEFORE any file change
- [ ] Ripple effects surfaced (components.button-primary references
      {colors.primary}, Colors prose, contrast of the new orange with
      on-primary #ffffff)
- [ ] Existing rationale updated, not deleted; new reaction recorded
- [ ] Validator re-run after the write, from the throwaway project's
      root: `uv run <plugin-root>/scripts/validate_design.py DESIGN.md`

## Fail modes to watch
- Token silently rewritten with no rendering
- on-primary left unreadable against the new orange with no mention
