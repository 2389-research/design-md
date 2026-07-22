---
version: alpha
name: PROJECT_NAME
description: One-line description of this design system.
colors:
  primary: "#4f46e5"
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

# PROJECT_NAME Design

## Overview

<!-- Brand personality, audience, emotional intent. 3-6 sentences.
     Include the WHY behind the overall direction, citing user reactions
     from the creation session, e.g.:
     "Dense, information-first layout: user rejected two airy variants as
     'too empty' and pointed at variant 3's tables as 'exactly right'." -->

## Colors

<!-- Semantic roles and usage rules for each palette entry. One line of
     rationale per choice. -->

## Typography

<!-- Font strategy and hierarchy. When to use each level. -->

## Layout

<!-- Grid model, spacing scale usage, density rules, containment. -->

## Elevation & Depth

<!-- Shadow/tonal strategy. DELETE if irrelevant (e.g., CLI-only project). -->

## Shapes

<!-- Corner radius philosophy. DELETE if irrelevant. -->

## Components

<!-- Styling guidance per component beyond the tokens: states, variants,
     when to use which. -->

## Terminal & CLI

<!-- EXTENSION SECTION (preserved by spec parsers). DELETE if project has
     no CLI/TUI surface. Cover: ANSI color usage (map to color tokens where
     possible), output density, progress/spinner conventions, error
     formatting, table-vs-prose bias, verbosity defaults. -->

## Voice & Copy

<!-- EXTENSION SECTION. Tone, error-message style, microcopy rules,
     naming conventions. Applies across every medium. -->

## Documents

<!-- EXTENSION SECTION. README/deck/one-pager aesthetics. DELETE if
     irrelevant. -->

## Do's and Don'ts

<!-- Practical guardrails. Include don'ts sourced from user rejections
     during creation ("Don't use gradients — user: 'looks like a crypto
     site'"). -->
