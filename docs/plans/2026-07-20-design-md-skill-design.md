# design-md Plugin — Design

<!-- ABOUTME: Validated design for the design-md plugin: skills + hooks that create, revise, and enforce a DESIGN.md file. -->
<!-- ABOUTME: Product of brainstorming session 2026-07-15..20; next step is a writing-plans implementation plan. -->

## Problem

AI agents produce visually inconsistent output unless given a persistent design reference. Non-designers — the people most reliant on agents for design — are the least able to articulate what they want in design vocabulary. And even when a design reference exists, agents routinely fail to consult it.

## Goals (priority order)

1. **Creation + Revision** — help anyone, especially non-designers, produce and evolve a DESIGN.md by *reacting to concrete variants* rather than describing in words.
2. **Enforcement** — when work touches anything user-visible, the agent loads DESIGN.md, builds against it, and self-checks before presenting.
3. Extraction from existing codebases is a *seeding input* to creation, not a standalone flow.

Not web-only: web/app UI first, CLI/TUI second, documents and voice/copy as riding-along sections.

## The artifact: DESIGN.md

- **Base format:** Google Labs DESIGN.md spec (alpha, Apache 2.0, `google-labs-code/design.md`). File at repo root. YAML front matter for machine-readable tokens (`name`, `colors`, `typography`, `spacing`, `rounded`, `components`, `{token.ref}` cross-references); markdown body for rationale in spec order (Overview → Colors → Typography → Layout → Elevation & Depth → Shapes → Components → Do's and Don'ts). Optional sections omitted when irrelevant.
- **Extensions** (legal — spec preserves unknown sections):
  - **Terminal & CLI** — ANSI color usage, output density, progress/spinner conventions, error formatting, table-vs-prose bias
  - **Voice & Copy** — tone, error-message style, microcopy rules, naming conventions
  - **Documents** — README/deck aesthetics where relevant
- **Reasoning discipline:** every choice carries a one-line *why*. User reactions captured during creation become the recorded rationale (e.g., "dense spacing: user rejected two airy variants as 'too empty'"). This gives enforcement something to reason with and gives revision memory of *why*.
- `[assumed]` One DESIGN.md per repo at root; no monorepo splitting in v1.

## Skill 1: `design-md` (create + revise)

One skill, two entry states, same loop.

**Phase 1 — Seed.** Cheap signal before generating:
- Named references ("2-3 sites/apps/CLIs you like"), translated to concrete attributes
- Micro-interview: ≤4 multiple-choice questions, every option anchored to a named familiar thing, never jargon ("Dense like a Bloomberg terminal / Airy like Apple.com / Between, like Stripe")
- Existing project UI/output harvested as signal (this is where extraction lives)
- Revision entry: seed = existing DESIGN.md + the prompting change

**Phase 2 — React.** Generate 3-4 divergent concrete variants in the project's medium:
- Web: one self-contained HTML gallery, same realistic content styled 3-4 ways, opened in browser
- CLI/TUI: script printing the same output (table, progress run, error) in 3-4 styles
- Ask for per-variant reactions; fragments fine ("2's colors, 1's density, hate all fonts")

**Phase 3 — Converge.** Merge reactions into a synthesized variant, show against runner-up. 1-2 rounds typical; user may stop anytime.

**Phase 4 — Write.** Emit spec-compliant DESIGN.md: tokens from the winning variant, reactions as rationale. Close with delta summary + single weakest assumption.

**Revision guard:** never silently rewrite tokens — show old vs new rendered side-by-side before writing; surface ripple effects ("primary color change affects components section").

`[assumed]` Variants are throwaway files in a scratch dir, never committed; DESIGN.md is the only artifact.

## Skill 2: `using-design` (enforcement)

1. Read DESIGN.md before writing code. Tokens are law; prose is judgment guidance.
2. Build with tokens by reference (CSS vars / theme constants matching front-matter names), never re-derived literal values.
3. Self-check before presenting (generate → check → correct): diff output against DESIGN.md — colors, type scale, spacing, Do's/Don'ts, voice — fix violations before the user sees them.
4. **Conform-or-surface:** if DESIGN.md can't express what's needed, don't improvise silently — propose a DESIGN.md addition. This is how the file evolves instead of rotting.

## Hooks

- **Pre (SessionStart + UserPromptSubmit):** if DESIGN.md exists, inject a short pointer: "this project has a DESIGN.md; invoke `using-design` before UI/output-styling work." No keyword heuristics — the skill decides whether work is design-touching.
- **Post (Stop):** inject audit prompt: "did this session change anything user-visible (UI, terminal output, copy)? If yes, verify conformance against DESIGN.md; report matches and divergences like a review comment." Divergences get fixed or explicitly flagged — never silent.
- No DESIGN.md → hooks inert. If substantial UI work starts without one, the skill may offer creation once — never nag.
- `[assumed]` Hooks ship with the plugin, not via user settings.json.

## Packaging

```
design/
  README.md
  skills/
    design-md/SKILL.md       # create + revise loop, per-medium variant guidance
    using-design/SKILL.md    # enforcement workflow
  hooks/
    hooks.json
    scripts/
  templates/
    DESIGN.template.md       # spec-compliant skeleton incl. extension sections
  evals/
```

Self-contained plugin (`design-md`), publishable both as a standalone repo/skills set and via the 2389 research marketplace. No dependency on jam/intent plugins (pattern-borrowing only); skill language stays generic — no 2389-internal jargon.

## Testing

- Hook scripts: real unit tests (DESIGN.md detection, injection output, inert path).
- Skills: scenario evals (e.g., "non-designer asks for 'something clean' → variants offered, not jargon questions"; "button color edit in DESIGN.md project → post-audit catches token violation").
- Validation: generated DESIGN.md parses against the Google spec — front-matter YAML validity, section ordering, token references resolve.

## NOT doing (v1)

- Standalone extraction skill (seeding only)
- Monorepo / multi-DESIGN.md support
- Figma/Stitch/design-tool integration — the file is the interface
- Google CLI/token tooling — we emit spec-compliant files; their tooling can consume them

## References

- https://github.com/google-labs-code/design.md (spec: docs/spec.md)
- https://getdesign.md/what-is-design-md — DESIGN.md catalog/ecosystem
- https://claude.com/product/design — generate → check-against-design-system → correct loop
