---
name: handdrawn-diagram
description: Create committable sketch-style architecture or flow diagrams as Mermaid handDrawn source plus verified SVG and PNG. Use for “손그림 다이어그램”, “스케치 아키텍처”, hand-drawn, handDrawn, or Devpost diagram requests. Do not use for ordinary charts or bitmap illustration.
---

# Hand-drawn Diagram

Create a legible diagram whose text survives rendering, including Korean and mixed CJK/Latin labels.

## Workflow

1. Confirm the system boundary, groups, flow direction, and output location from context. Keep the smallest useful node set.
2. Author Mermaid with `look: handDrawn`, quoted labels, semantic group colors, and short text.
3. Prefer a repository-installed Mermaid CLI. If none exists, explain that `npx -y` may download packages and request approval before network installation.
4. Render both SVG and PNG using [render guide](references/rendering.md).
5. Inspect the PNG visually. Check clipped Korean/English labels, overlaps, contrast, arrow direction, and group meaning. Revise and rerender until legible.
6. Return links to source, SVG, and PNG plus the render command used. Do not commit unless separately requested.

Avoid hand-editing generated SVG when the Mermaid source can be corrected instead.
