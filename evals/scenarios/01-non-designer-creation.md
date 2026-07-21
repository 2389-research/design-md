# 01 — Non-designer creation

## Setup
Empty project directory with a minimal web app (one HTML page, no styling
direction). Plugin installed.

## Prompt
"I want this to look nice and clean but I'm honestly bad at design.
Can you set up a design for this project?"

## Pass criteria
- [ ] design-md skill invoked (not ad-hoc styling)
- [ ] Seeding questions are ≤4, multiple-choice, anchored to named
      familiar products; zero design jargon in questions
- [ ] 3-4 genuinely divergent variants rendered as a self-contained HTML
      gallery and opened in the browser
- [ ] User reactions requested as point-at-things, fragments welcomed
- [ ] DESIGN.md written at project root, passes validate_design.py
- [ ] Rationale lines cite the user's actual reactions
- [ ] Variants left in scratch dir, not committed

## Fail modes to watch
- Asks "what fonts/colors do you want?" (introspection, not reaction)
- Variants differ only trivially (same layout, four accent colors)
- DESIGN.md written without any variant round
