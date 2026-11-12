# design-md

Design and implementation plans for a plugin that helps people create and revise a repository's `DESIGN.md`, then guides agents to follow it when changing visible output.

## Status

This repository currently contains planning documents only. It does not yet contain installable skills, hook scripts, templates, or a test harness. The package layout and commands in the plans describe work to implement, not an available release.

## Reading the plans

- [Plugin design](docs/plans/2026-07-20-design-md-skill-design.md): the create/revise loop, `using-design` enforcement, hook behavior, artifact format, and scope.
- [Implementation plan](docs/plans/2026-07-20-design-md-plugin.md): proposed files, task sequence, and verification steps.

Start with the design to understand the intended behavior, then use the implementation plan as a development checklist. There is no setup or runtime command for this checkout yet.
