<!-- ABOUTME: Eval scenario — revising colors.primary in an existing DESIGN.md must surface ripple effects before any write. -->
<!-- ABOUTME: Pass = side-by-side render, referencing components and contrast flagged, rationale preserved; fail = silent token rewrite. -->

# 03 — Revision ripple

## Setup
Throwaway project with a committed DESIGN.md. Copy
`evals/fixtures/03-ripple-demo-DESIGN.md` into the throwaway project as
`DESIGN.md` and commit it, so the pre-revision state is a clean baseline
to diff against.

**Do not build this fixture from `templates/DESIGN.template.md`.** The
template's prose sections are guidance comments, not rationale, so a run
seeded from it cannot test the "rationale preserved, not deleted" pass
criterion below — there is no rationale to delete. The fixture carries
six verbatim user reactions for exactly that reason.

The fixture sets `colors.primary` to `#2563EB` and `colors.on-primary`
to `#ffffff`, and its `components.button-primary` references both via
`{colors.primary}` / `{colors.on-primary}` — so a primary-color change
must surface that component ripple and the on-primary contrast question.
It also documents `error` as "visibly distinct from primary", which a
warm orange crowds; surfacing that collision is a bonus, not required.

## Prompt
"Actually I think the primary color should be a warm orange instead."

## Pass criteria
- [ ] design-md skill revision flow: current vs proposed rendered side
      by side BEFORE any file change
- [ ] Ripple effects surfaced (components.button-primary references
      {colors.primary}, Colors prose, contrast of the new orange with
      on-primary #ffffff)
- [ ] Existing rationale updated, not deleted; new reaction recorded.
      Check all six seeded quotes survive: "too consumer", "boring in the
      right way", "harsh on a white field", "crypto site", "pages you at
      3am", "I compare rows". Grep for them with newlines collapsed —
      line wrapping splits the phrases in the written file.
- [ ] DESIGN.md edited in place, not recreated from the template
      (unrelated sections and tokens still present afterward)
- [ ] Validator re-run after the write, from the throwaway project's
      root: `uv run <plugin-root>/scripts/validate_design.py DESIGN.md`

## Fail modes to watch
- Token silently rewritten with no rendering
- on-primary left unreadable against the new orange with no mention
