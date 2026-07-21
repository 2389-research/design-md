# 02 — Enforcement + token violation

## Setup
Project with a committed DESIGN.md (use templates/DESIGN.template.md
filled with concrete values) and a small web page that uses its tokens.

## Prompt
"Add a signup banner to the top of the page with a nice green call-to-action
button."

(Note: DESIGN.md defines no green; primary is indigo.)

## Pass criteria
- [ ] Pre-hook pointer appears in context; using-design skill invoked
      before edits
- [ ] Agent either uses colors.primary for the CTA or surfaces the gap
      explicitly ("no green token — options: ...") — it does NOT silently
      hardcode a green hex
- [ ] Self-check report appears before presenting ("Design check: ...")
- [ ] Stop-hook audit runs after the turn and its conclusion matches
      reality

## Fail modes to watch
- Banner built with literal colors despite DESIGN.md
- Audit reports "conforms" when a divergence exists
- Audit loops (stop_hook_active guard failing)
