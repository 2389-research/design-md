<!-- ABOUTME: Eval scenario — hooks and using-design skill enforce DESIGN.md tokens when the user asks for an off-palette color. -->
<!-- ABOUTME: Pass = agent uses colors.primary or surfaces the gap; fail = silently hardcoded green hex or a false "conforms" audit. -->

# 02 — Enforcement + token violation

## Setup
Throwaway project with a committed DESIGN.md and a small web page that
uses its tokens. To build the DESIGN.md, copy the plugin's
`templates/DESIGN.template.md` into the throwaway project as `DESIGN.md`
and replace `PROJECT_NAME` with a real name (e.g. `signup-demo`). Keep
the template's token values as-is — in particular:

- `colors.primary: "#4f46e5"` (indigo)
- `colors.on-primary: "#ffffff"`

The palette must define no green token; the indigo primary is what makes
the "green button" request below a violation.

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
