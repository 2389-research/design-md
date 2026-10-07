<!-- ABOUTME: Index of manually-run acceptance scenarios for the design-md plugin. -->
<!-- ABOUTME: Explains the scenario file format (setup / prompt / pass criteria) and where to record results. -->

# design-md Evals

Scenario-based evaluations. Each scenario file defines: setup, the prompt
to give a fresh Claude Code session with this plugin installed, and pass
criteria. Run them manually or via a driver agent; record results in
`evals/results/<scenario>/<date>.md`.

Drive them in a real interactive session (a dedicated tmux window works
well) rather than `claude -p` — print mode hides mid-turn behavior, which
is where most of the signal is. Isolate `XDG_STATE_HOME` so the creation
offer's markers do not touch your real state directory.

| # | Scenario | Exercises |
|---|----------|-----------|
| 01 | Non-designer creation | design-md skill, Phases 1-4 |
| 03 | Revision ripple | design-md revision guard |

Scenario 02 (enforcement + token violation) was removed along with the
`using-design` skill and the pointer/audit hooks — see
`results/ab-messy-codebase/` for the eval that retired them.

## Recorded results

- `results/03-revision-ripple/` — revision guard, including the contrast
  catch (refused a warm orange that failed DESIGN.md's own white-text
  contrast rule at 3.56:1).
- `results/ab-messy-codebase/` — four-arm A/B on a deliberately drifted
  codebase, measuring off-token colors introduced while adding a feature.
  This is the eval that scoped the plugin down to creation.
