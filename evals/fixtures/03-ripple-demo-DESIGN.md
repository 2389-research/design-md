---
version: alpha
name: ripple-demo
description: Design system for ripple-demo, a small internal status dashboard.
colors:
  primary: "#2563EB"
  on-primary: "#ffffff"
  surface: "#ffffff"
  on-surface: "#1f2937"
  neutral: "#6b7280"
  error: "#dc2626"
typography:
  headline-lg:
    fontFamily: "Inter, sans-serif"
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
  body-md:
    fontFamily: "Inter, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: "Inter, sans-serif"
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.3
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
rounded:
  sm: 4px
  md: 8px
  full: 9999px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm} {spacing.md}"
---

# ripple-demo Design

## Overview

ripple-demo is an internal status dashboard for an on-call engineering team.
The audience is technical and time-pressured: people land here mid-incident and
need to read state in under five seconds. The direction is calm and utilitarian
— dense information, no decoration that doesn't carry meaning. During creation
the user rejected two softer variants as "too consumer, this isn't a product
tour" and pointed at the flat blue-on-white variant as "boring in the right
way." Color is reserved for status and action; everything else stays neutral so
that anything colored reads as signal.

## Colors

- `primary` `#2563EB` — the single action/identity color. Chosen because the
  user reacted to the cooler blue over a purple candidate: "purple reads
  playful, I want this to read like infrastructure." Used for primary buttons,
  active nav, and focus rings. Never used for decorative fills.
- `on-primary` `#ffffff` — text and icons on primary surfaces. White was kept
  deliberately: the user wanted maximum contrast on action surfaces after
  squinting at a tinted-label variant and saying "I can't read that at a
  glance."
- `surface` `#ffffff` / `on-surface` `#1f2937` — the default reading pair. Near
  black rather than pure black, which the user found "harsh on a white field."
- `neutral` `#6b7280` — secondary text, borders, disabled states.
- `error` `#dc2626` — failure states only. Kept visibly distinct from primary
  so a red badge never gets mistaken for an action.

## Typography

Inter throughout — the user rejected a serif pairing as "editorial, wrong
genre." `headline-lg` for page titles only, `body-md` as the default reading
size, `label-sm` for table headers, badges, and metadata. No size between
body-md and headline-lg: the user disliked a three-tier heading variant as
"more hierarchy than we have content."

## Layout

Single 12-column grid, `spacing.md` gutters, `spacing.lg` between major
sections. Density is the point — the user's strongest reaction in creation was
against whitespace ("stop making me scroll for four numbers"). Cards contain
related state; unrelated state gets a rule, not a card.

## Elevation & Depth

Flat by default. A 1px `neutral` border does the containment work that a shadow
would elsewhere. Shadows are reserved for genuinely floating surfaces (menus,
dialogs) — the user called a shadowed-card variant "puffy."

## Shapes

`rounded.sm` on inputs and badges, `rounded.md` on buttons and cards,
`rounded.full` on status dots only. The user rejected fully-pill buttons as
"too friendly for a thing that pages you at 3am."

## Components

- `button-primary` — the only filled button. One per view; everything else is a
  text or bordered button. Hover darkens the background, focus shows a 2px
  `primary` ring offset by 2px.
- Status badge — `label-sm` on a tinted background, `rounded.sm`. Color comes
  from status semantics, never from primary.
- Table — the default container for lists. The user chose tables over card grids
  in creation: "I compare rows, I don't browse."

## Voice & Copy

Terse and factual. Errors say what happened and what to do next, in that order,
with no apology ("Deploy failed — check the build log" not "Sorry, something
went wrong!"). Never use exclamation marks. Label buttons with the verb of the
action, not "Submit".

## Do's and Don'ts

- **Do** reserve `primary` for action and identity — if everything is blue,
  nothing is.
- **Do** keep white text on primary surfaces; contrast on action targets is
  non-negotiable per the creation session.
- **Don't** add gradients. The user rejected a gradient header outright: "looks
  like a crypto site."
- **Don't** introduce a new color to signal a new concept — earn it with a
  badge or a label first.
- **Don't** pad your way out of a layout problem; density was the explicit ask.
