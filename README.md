<!-- ABOUTME: README for the design-md Claude Code plugin: create, revise, and enforce a DESIGN.md design system file. -->
<!-- ABOUTME: Covers what the plugin does, the two skills, hook behavior, installation, repo layout, tests, and license. -->

# design-md

A Claude Code plugin that helps you — especially if you are not a designer —
create and evolve a `DESIGN.md` design-reference file for your project, and
then makes sure agents actually use it when building anything user-visible.

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

1. **Create and revise by reaction, not description.** The `design-md`
   skill never asks you to articulate design in words. It shows you 3-4
   concretely rendered, genuinely divergent variants and asks you to point
   at what you like and hate. Your reactions become the tokens and the
   recorded rationale in DESIGN.md.
2. **Enforce during building.** The `using-design` skill plus three hooks
   keep agents loading DESIGN.md before user-visible work, building with
   token references instead of literal values, and auditing their own
   output against the file before you see it.

## The two skills

### `design-md` — create or revise DESIGN.md

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

Revision mode never silently rewrites tokens: it renders current vs
proposed side by side, surfaces ripple effects ("changing `colors.primary`
affects `components.button-primary`"), and re-validates after every change.

### `using-design` — build against DESIGN.md

Invoked before any work that changes user-visible output:

- **Load** DESIGN.md first. Tokens are law; prose is judgment.
- **Build with tokens by reference** (CSS custom properties / theme
  constants named after the tokens), never re-derived approximations.
- **Self-check before presenting**: diff the output against DESIGN.md
  (colors, type levels, spacing, radii, Do's and Don'ts, voice, terminal
  conventions) and fix violations before the user sees the result.
- **Conform or surface**: if DESIGN.md can't express what's needed, build
  as close as possible, flag the gap explicitly, and propose a DESIGN.md
  addition — never improvise silently.

If a project has no DESIGN.md and substantial user-visible work is
starting, the skill offers once to create one, then drops it if declined.

## Hooks

Defined in `hooks/hooks.json`. All three detect DESIGN.md by walking up
from the working directory, stopping at the repository root. Without a
DESIGN.md the audit hook is fully inert, and the context hook injects only
a small conditional note on each prompt: the hook does no keyword matching —
the model judges from full conversation context whether the request is
design work, and only then offers `design-md` once. The note names a marker
file under `$XDG_STATE_HOME/design-md/` that the model touches afterward
(accepted or declined), permanently silencing the note for that project.

| Event | Script | Behavior |
|---|---|---|
| `SessionStart` | `hooks/scripts/design_context.py` | Injects a one-line pointer: DESIGN.md exists, invoke `using-design` before user-visible work. |
| `UserPromptSubmit` | `hooks/scripts/design_context.py` | Same pointer, refreshed each prompt. With no DESIGN.md: conditional creation note the model acts on only for design work, self-silenced via marker. |
| `Stop` | `hooks/scripts/design_audit.py` | If the turn modified files via Edit/Write/NotebookEdit, blocks once with an audit prompt: review the changes against DESIGN.md like a code review, fix or explicitly flag divergences. Does not re-fire on its own continuation. |

## The template and its extension sections

`templates/DESIGN.template.md` is a skeleton compliant with the Google Labs
spec: token front matter plus prose sections in spec order (Overview,
Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and
Don'ts). It adds three extension sections, preserved by spec parsers:

- **Terminal & CLI** — ANSI color usage mapped to tokens, output density,
  progress conventions, error formatting.
- **Voice & Copy** — tone, error-message style, microcopy rules.
- **Documents** — README/deck/one-pager aesthetics.

Sections irrelevant to a project's media are deleted during creation.

## Validator

`scripts/validate_design.py` checks a DESIGN.md for: valid YAML front
matter, the required `name` field, resolvable `{token.ref}` references, and
duplicate section headings.

```bash
uv run --with pyyaml -- python3 scripts/validate_design.py DESIGN.md
```

Prints `OK` and exits 0 on success; prints issues and exits 1 otherwise.

## Installation

**From a marketplace** (if this plugin is listed in one you've added):

```
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

```
.claude-plugin/plugin.json      Plugin manifest (design-md, v0.1.0, MIT)
skills/design-md/SKILL.md       Create/revise skill (Seed → React → Converge → Write)
skills/using-design/SKILL.md    Enforcement skill (load, build with tokens, self-check)
hooks/hooks.json                Hook wiring (SessionStart, UserPromptSubmit, Stop)
hooks/scripts/design_context.py Pointer-injection hook script
hooks/scripts/design_audit.py   Post-turn conformance audit hook script
templates/DESIGN.template.md    Spec-compliant DESIGN.md skeleton + extension sections
scripts/validate_design.py      DESIGN.md validator
evals/                          Manually-run acceptance scenarios
tests/                          pytest suite for hooks and validator
docs/plans/                     Design and implementation plans
```

## Running the tests

```bash
uv run --with pytest --with pyyaml -- pytest tests/ -v
```

The `evals/` directory holds three scenario docs (non-designer creation,
enforcement with a token violation, revision ripple) that are run manually
against a live Claude Code session with the plugin installed — see
`evals/README.md`.

## License

MIT — see [LICENSE](LICENSE).
