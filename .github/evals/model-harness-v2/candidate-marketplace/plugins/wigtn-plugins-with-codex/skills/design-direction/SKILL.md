---
name: design-direction
description: Derive a project-native visual direction for a new UI or redesign by inspecting the existing design system first. Use for UI design direction, style exploration, greenfield interface styling, or redesign requests. Do not use for a tiny CSS fix, established-component implementation, or non-UI work.
---

# Design Direction

Prefer the product’s existing visual language over a generic style preset.

## Workflow

1. Inspect tokens, global styles, fonts, representative pages, shared components, spacing, icons, and motion.
2. If a coherent system exists, summarize it and produce an implementation contract that extends it. Do not offer unrelated styles.
3. For greenfield work or an explicit redesign, present two or three genuinely distinct directions with tradeoffs. Let the user choose when the choice materially changes the product.
4. Read only the selected reference from `references/styles/`, plus common references that apply.
5. Produce a short contract covering typography, palette roles, spacing rhythm, surfaces, borders, interaction states, motion, accessibility, and anti-patterns.
6. Do not implement unless requested.

Available references are indexed in [style index](references/style-index.md). They are inspiration and constraints, not a license to overwrite repository conventions.
