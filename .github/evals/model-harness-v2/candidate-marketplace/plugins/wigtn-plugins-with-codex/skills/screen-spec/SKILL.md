---
name: screen-spec
description: Create implementation-ready IA, user flow, screen specification, lo-fi HTML wireframe, and developer handoff from a PRD or feature description. Use for “화면정의서”, “IA”, “user flow”, “wireframe”, or UI handoff requests. Do not use for visual styling alone or non-UI backend work.
---

# Screen Spec

Create five connected artifacts under `docs/product/screens/<feature>/`:

1. `01-IA.md`
2. `02-USER-FLOW.md`
3. `03-SCREEN-SPEC.md`
4. `04-WIREFRAME.html`
5. `05-DEV-HANDOFF.md`

## Workflow

1. Read the source PRD or feature description and existing routes, components, permissions, and design system.
2. Preserve requirement IDs. Record safe inferences under `Assumptions`; ask only when a missing decision materially changes navigation or behavior.
3. Build the artifacts in order. Keep page IDs, route names, roles, and state names consistent across all five.
4. Cover states that apply: loading, empty, error, success, unauthorized, validation, offline, and destructive confirmation.
5. Keep the wireframe grayscale with semantic status colors only. It validates structure and interaction, not brand direction.
6. If browser control is available, open the HTML and verify desktop and mobile widths, overflow, readable labels, and navigational links. Fix discovered defects before reporting completion.
7. Return file links and verification results without pasting every artifact into the conversation.

Use the templates in `assets/templates/`. Read [state checklist](references/state-checklist.md) while writing screen states and [handoff checklist](references/handoff-checklist.md) before completion.

Do not invent a visual brand. If a new visual direction is needed, suggest `design-direction` after the structural spec is complete.
