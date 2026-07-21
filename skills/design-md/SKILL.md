---
name: design-md
description: Use when creating or updating a DESIGN.md design system file, when the user wants to define how their project should look and feel, or when they express design desires they can't articulate ("make it look nice", "something clean", "I don't like it but can't say why"). Extracts design taste through concrete variants the user reacts to — no design vocabulary required. Triggers on "design.md", "DESIGN.md", "design system", "visual identity", "style this project", "make it look".
---

# design-md: Create or Revise a DESIGN.md

Produce a DESIGN.md — a machine-and-human-readable design system file
(Google Labs DESIGN.md spec) — by showing the user concrete rendered
variants and capturing their reactions. Never ask a non-designer to
describe design in words; show them things and let them point.

**Core rule: taste is extracted by reaction, not introspection.**

## Entry states

- **Create:** no DESIGN.md exists. Run all four phases.
- **Revise:** DESIGN.md exists and the user wants a change ("darker",
  "less cramped", "new brand color"). Seed = current DESIGN.md + the
  requested change; run Phases 2-4 scoped to what's changing.

## Phase 1 — Seed (cheap signal before generating anything)

Collect, in one short exchange each (skip any that are already answered):

1. **References:** "Name 2-3 sites, apps, or CLIs whose look you like —
   or hate." Translate names into concrete attributes yourself (Linear →
   dark, dense, keyboard-first; Stripe → airy, generous whitespace,
   restrained color).
2. **Micro-interview:** at most 4 multiple-choice questions. Every option
   MUST be anchored to a named familiar thing, never jargon:
   - "Dense like a Bloomberg terminal / airy like Apple.com / between,
     like Stripe?"
   - "Colorful like Figma / restrained like Notion / monochrome + one
     accent like Linear?"
   Never ask "what typography do you want?" or use terms like
   "elevation", "tonal", "grid system" in questions.
3. **Existing output:** if the project already renders anything (UI
   pages, CLI output, README), capture it and treat it as an implicit
   reference — extract its current palette/density/tone as one seed
   among others.

Do not skip to Phase 2 with zero signal; one reference or one answered
question is enough.

## Phase 2 — React (generate divergent variants)

Generate 3-4 genuinely divergent variants in the project's medium, in a
scratch directory (`/tmp/design-md-<project>/` or similar). Variants are
throwaway; only DESIGN.md is ever committed.

**Web/app UI:** one self-contained HTML file (`gallery.html`, no external
dependencies, system/web-safe font stacks or embedded @font-face) showing
the SAME realistic page content styled 3-4 ways, clearly labeled
Variant 1..4. Use content from the actual project when possible (its real
nav items, real data). Open it in the user's browser.

**CLI/TUI:** one script (bash or python) that prints the SAME output — a
table, a progress run, an error message — in 3-4 styles varying color
usage, density, ornamentation (rules/boxes vs bare), and tone. Run it so
the user sees real terminal rendering.

**Documents:** 3-4 renderings of the same one-pager/README section.

Variants must disagree with each other on real axes (density, color
temperature, ornament, formality). Four near-identical variants teach
nothing.

**Ask for reactions, not descriptions:** "Point at anything you like or
hate, per variant. Fragments are perfect: '2's colors, 1's density, hate
all the fonts' is a great answer."

## Phase 3 — Converge

Synthesize reactions into one merged variant; render it next to the
closest runner-up and ask again. Typical session: 1-2 rounds. The user
can stop at any time ("that one") — never force another round. If
reactions conflict ("liked 1's density" + "liked 3's whitespace"),
render the tension as two sub-variants rather than asking them to
resolve it verbally.

## Phase 4 — Write

1. Copy `templates/DESIGN.template.md` (in this plugin) to `DESIGN.md`
   at the project root.
2. Fill YAML front matter with tokens extracted from the winning
   variant: colors, typography levels, spacing scale, rounded scale,
   component tokens (use `{token.ref}` cross-references).
3. Fill prose sections. **Every choice gets a one-line why, and user
   reactions ARE the rationale:** "Dense layout: user rejected two airy
   variants as 'too empty'." Rejections go in Do's and Don'ts:
   "Don't use gradients — user: 'looks like a crypto site'."
4. Delete sections irrelevant to the project's media, and delete all
   template guidance comments.
5. Validate: run the plugin's `scripts/validate_design.py DESIGN.md`.
   Fix any issues before presenting.
6. Close with a delta summary (what the design says in 3 lines) plus the
   single weakest assumption, asked once. No confirmation checklists.

## Revision rules

- Never silently rewrite tokens. Render current vs proposed side by side
  (same gallery/script mechanism, 2 variants) before writing.
- Surface ripple effects: "changing colors.primary affects
  components.button-primary and the Colors prose."
- Preserve existing rationale lines unless the user's new reaction
  contradicts them — then update the rationale, citing the new reaction.
- Re-run the validator after every revision.

## Non-designer principles (apply throughout)

- Multiple choice over open-ended; named references over adjectives;
  reactions over descriptions.
- Fragments and negative reactions are first-class data. "I hate it" is
  a fine start — render the opposite and ask again.
- Never use design jargon in a question. Using it in DESIGN.md prose is
  fine — that file is for agents too.
- One question per message during seeding.
