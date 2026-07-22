---
name: using-design
description: Use before any work that changes user-visible output — UI, styling, components, pages, terminal/CLI output, or user-facing copy. If the project contains a DESIGN.md, loads it, builds with its tokens, and self-checks the result against it before presenting; if it doesn't, offers once to create one. Also invoked by the design-md plugin hooks.
---

# using-design: Build Against DESIGN.md

When work touches anything a user will see, DESIGN.md is the contract.
Read it, build with it, and check your output against it BEFORE the user
sees the result.

## Step 1 — Load

Read `DESIGN.md` at the project root before writing any code.

- **Tokens are law:** front-matter values (colors, typography, spacing,
  rounded, components) are exact. Never eyeball-approximate them.
- **Prose is judgment guidance:** Overview, section rationale, and
  Do's and Don'ts tell you how to apply tokens to situations the tokens
  don't literally cover.

If the work clearly touches nothing user-visible (pure backend logic,
build config, tests), say so in one line and proceed without the rest of
this workflow.

## Step 2 — Build with tokens by reference

- Web: consume tokens as CSS custom properties / theme constants named
  after the front-matter tokens (`--color-primary`, `--spacing-md`). If
  the project has no token layer yet, create one from the front matter
  rather than scattering literals.
- Never re-derive values ("that's roughly #4f46e5") — copy the token.
- CLI/TUI: follow the Terminal & CLI section for color usage, density,
  progress conventions, and error formatting.
- Copy/microcopy: follow Voice & Copy for tone and error style.
- New component? Check the Components section and existing component
  tokens for the nearest precedent before inventing.

## Step 3 — Self-check before presenting

After building, diff your output against DESIGN.md and fix violations
BEFORE showing the user (skip items whose sections or tokens the
project's DESIGN.md doesn't define):

- [ ] Every color used is a token (or derived per an explicit rule in
      the prose)
- [ ] Type sizes/weights map to defined typography levels
- [ ] Spacing values come from the spacing scale
- [ ] Corner radii come from the rounded scale
- [ ] Nothing violates Do's and Don'ts
- [ ] User-facing text matches Voice & Copy
- [ ] Terminal output matches Terminal & CLI

Fix what you find. Then report in one or two lines: "Design check:
conforms" or "Design check: 2 divergences fixed (off-scale padding,
non-token gray)."

## Step 4 — Conform or surface (never improvise silently)

If DESIGN.md genuinely cannot express what's needed — a new component
with no precedent, a missing semantic color, a medium it doesn't cover:

1. Build it as close to the existing system as possible.
2. Surface the gap explicitly: "DESIGN.md has no 'warning' color; I used
   colors.error at 60% as a stopgap. Proposed addition: ..."
3. Offer to update DESIGN.md via the design-md skill (revision flow).

Divergence is allowed only when explicit. Silent divergence is the
failure mode this skill exists to prevent.

## No DESIGN.md?

If substantial user-visible work is starting and the project has no
DESIGN.md, offer ONCE: "This project has no DESIGN.md — want to create
one first so this and future work stays consistent? (design-md skill,
~10 minutes)." If declined, proceed and do not ask again this session.

If a hook note in the conversation names a silence-marker path for this
offer, touch that marker once the offer resolves — accepted or declined —
so the note never repeats for this project.
