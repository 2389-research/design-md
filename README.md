<!-- ABOUTME: README for the design-md Claude Code plugin: create, capture, and revise a DESIGN.md design system file. -->
<!-- ABOUTME: Covers what the plugin does, the skill, the creation-offer hook, installation, repo layout, tests, and license. -->

# design-md

A Claude Code plugin that helps you — especially if you are not a designer —
create and evolve a `DESIGN.md` design-reference file for your project.

It works across media: web UI, CLI/TUI output, documents (READMEs, decks,
one-pagers), and voice/copy. It is not web-only.

## What is DESIGN.md?

[DESIGN.md](https://github.com/google-labs-code/design.md) is a Google Labs
spec for a machine-and-human-readable design system file that lives at your
project root. It combines:

- **YAML front matter** — exact design tokens: colors, typography levels,
  spacing scale, corner radii, component tokens (with `{token.ref}`
  cross-references).
- **Prose sections** — the judgment layer: overview, rationale per choice,
  and Do's and Don'ts.

Agents read the tokens as law and the prose as guidance, so output stays
consistent across sessions and contributors.

## What this plugin does

**Creates the file, by reaction rather than description.** The `design-md`
skill never asks you to articulate design in words. It shows you 3-4
concretely rendered, genuinely divergent variants and asks you to point at
what you like and hate. Your reactions become the tokens and the recorded
rationale in DESIGN.md.

**It does not police adherence, on purpose.** An earlier version shipped a
`using-design` enforcement skill plus pointer and audit hooks. A four-arm
A/B on a deliberately drifted codebase removed them: an agent with DESIGN.md
and *no plugin at all* found the file unprompted, surfaced its own judgment
calls, and introduced zero off-token colors — matching the full enforcement
stack exactly, while agents without the file introduced one to two. The
artifact does the work; the enforcement layer did not earn its cost. See
`evals/results/` for the numbers.

## The skill: `design-md`

Three entry states:

- **Create** — no DESIGN.md, no established look worth keeping. Run all four
  phases.
- **Capture** — no DESIGN.md but the project already has a visual system in
  its code. The job is transcription, not invention: read the stylesheets
  and write down what is already true.
- **Revise** — DESIGN.md exists and something should change.

Four phases:

- **Seed** — asks for 2-3 reference products you like or hate, plus at most
  4 multiple-choice questions where every option is anchored to a named
  familiar product ("dense like a Bloomberg terminal / airy like Apple.com"),
  never design jargon.
- **React** — generates 3-4 divergent variants in your project's medium:
  a self-contained HTML gallery for web/app UI, a script that prints the
  same output in 3-4 styles for CLI/TUI, or multiple renderings for
  documents. Variants are throwaway; only DESIGN.md is committed.
- **Converge** — merges your reactions into one variant, renders it against
  the runner-up, and repeats for 1-2 rounds (you can stop any time).
- **Write** — fills the template with tokens from the winning variant and
  prose where your reactions ARE the rationale ("Don't use gradients —
  user: 'looks like a crypto site'"), then runs the validator.

**Every token must trace to a source** — a rule in the winning variant, or a
value in the codebase when capturing. Slots with no source are deleted, not
filled with plausible values: beyond front matter and `name`, the validator
requires no particular token, and an invented one is indistinguishable to
the next agent from one you chose.

Revision mode never silently rewrites tokens: it renders current vs
proposed side by side, surfaces ripple effects ("changing `colors.primary`
affects `components.button-primary`"), and re-validates after every change.

## The hook

One hook, defined in `hooks/hooks.json`, covering the one thing an agent
cannot discover on its own — a design system that does not exist yet.

| Event | Script | Behavior |
|---|---|---|
| `UserPromptSubmit` | `hooks/scripts/design_offer.py` | With no DESIGN.md in the repo: injects a small conditional note on the first prompt of each session. Silent whenever a DESIGN.md already exists. |

The hook does no keyword matching. It judges nothing about the prompt — the
model reads the note and decides from full conversation context whether the
request is design work, offering `design-md` once if so. The note names a
marker file under `$XDG_STATE_HOME/design-md/` that the model touches once
the offer resolves (accepted *or* declined), permanently silencing it for
that project.

This exists because skill-side discovery measurably fails: in a live test on
a real site, a full UI-heavy session — colors, cards, masks, an aesthetic
question asked out loud — never once surfaced DESIGN.md without it.

## The template and its extension sections

`templates/DESIGN.template.md` is a skeleton compliant with the Google Labs
spec: token front matter plus prose sections in spec order (Overview,
Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and
Don'ts). It adds three extension sections, preserved by spec parsers:

- **Terminal & CLI** — ANSI color usage mapped to tokens, output density,
  progress conventions, error formatting.
- **Voice & Copy** — tone, error-message style, microcopy rules.
- **Documents** — README/deck/one-pager aesthetics.

Sections irrelevant to a project's media are deleted during creation. So are
token slots with no source — the template is a menu, not a form.

## Validator

`scripts/validate_design.py` checks a DESIGN.md for:

- **Front matter is present and closed.** A file with no front matter, or
  one opened with `---` and never closed, is rejected — both carry no
  tokens, and the unterminated case previously slipped through as "no front
  matter" and silently skipped every check below.
- **Valid YAML mapping** with the required `name` field.
- **Resolvable `{token.ref}` references.**
- **No duplicate section headings**, counting the spec's aliases as the same
  section: `Brand & Style` = `Overview`, `Layout & Spacing` = `Layout`,
  `Elevation` = `Elevation & Depth`.

```bash
uv run --with pyyaml -- python3 scripts/validate_design.py DESIGN.md
```

Prints `OK` and exits 0 on success; prints issues and exits 1 otherwise.

## Installation

**From a marketplace** (if this plugin is listed in one you've added):

```text
/plugin install design-md@<marketplace-name>
```

**Manually**, clone this repository and either load it for a session:

```bash
git clone <this-repo> design-md
claude --plugin-dir ./design-md
```

or use the interactive `/plugin` manager inside Claude Code to add a
marketplace that lists it and install from there.

## Repository layout

```text
.claude-plugin/plugin.json      Plugin manifest (design-md, v0.2.0, MIT)
skills/design-md/SKILL.md       Create/capture/revise skill (Seed → React → Converge → Write)
hooks/hooks.json                Hook wiring (UserPromptSubmit)
hooks/scripts/design_offer.py   One-time DESIGN.md creation offer
templates/DESIGN.template.md    Spec-compliant DESIGN.md skeleton + extension sections
scripts/validate_design.py      DESIGN.md validator
evals/                          Manually-run acceptance scenarios and recorded results
tests/                          pytest suite for the hook and validator
docs/plans/                     Design and implementation plans
```

## Running the tests

```bash
uv run --with pytest --with pyyaml -- pytest tests/ -v
```

`evals/` holds scenario docs run manually against a live Claude Code session
with the plugin installed, plus recorded results from past runs — see
`evals/README.md`.

## License

MIT — see [LICENSE](LICENSE).
