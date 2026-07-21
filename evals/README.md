# design-md Evals

Scenario-based evaluations. Each scenario file defines: setup, the prompt
to give a fresh Claude Code session with this plugin installed, and pass
criteria. Run them manually or via a driver agent; record results in
`evals/results/<scenario>/<date>.md`.

| # | Scenario | Exercises |
|---|----------|-----------|
| 01 | Non-designer creation | design-md skill, Phases 1-4 |
| 02 | Enforcement + token violation | hooks, using-design self-check |
| 03 | Revision ripple | design-md revision guard |
