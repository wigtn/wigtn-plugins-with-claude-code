# Terminal / Hacker Style Guide

## Core Philosophy
- The interface IS the command line — elevated to art
- Information density is a virtue, not a problem
- Monospace is not a constraint, it is the medium
- Every element earns its place through function
- Dark by nature, not by trend
- Speed of comprehension over visual beauty

---

## Core Characteristics

| Aspect | Description |
|--------|-------------|
| Feel | Technical, focused, hacker-elite, utilitarian-beautiful |
| Colors | Dark base, phosphor green/amber/cyan accents, status-driven |
| Typography | Monospace dominant, ligatures encouraged |
| Spacing | Compact, grid-aligned, information-dense |
| Borders | Thin, consistent, often dashed or ASCII-inspired |
| Shadows | Minimal — CRT glow optional, never box-shadow decorative |
| Motion | Typewriter effects, cursor blink, scan lines — functional not decorative |

---

## Terminal/Hacker vs Related Styles

| | Terminal/Hacker | Dark Mode First | Retro Pixel |
|--|----------------|-----------------|-------------|
| Era | Modern (2024+) | Modern | 1980s-90s |
| Font | Monospace everywhere | Sans + mono mix | Pixel fonts |
| Color Logic | Semantic (green=ok, red=error) | Aesthetic (neon accents) | CRT emulation |
| Density | High, dashboard-like | Standard spacing | Pixel-grid |
| Chrome | Minimal — tabs, status bars | Cards, modals | Scanlines, CRT curve |
| Reference | Warp, Ghostty, Linear CLI, Fig | Vercel, VS Code dark | MS-DOS, Commodore |
| Audience | Power users, developers | General tech users | Nostalgia, gaming |

---

## AI Slop Prevention Warning

- DO NOT just make everything green-on-black and call it "hacker"
- DO NOT use Matrix rain animations — it's 2026, not 1999
- DO NOT sacrifice readability for aesthetic — this style VALUES readability
- DO NOT forget that real terminals have sophisticated color systems (256-color, ANSI)
- DO NOT mix decorative fonts in — monospace is sacred, only weight/size varies

**This is modern terminal craft, not a movie prop.**

---

## Color Palette

### Phosphor Green (Classic)
```css
:root {
  /* Backgrounds */
  --term-bg: #0c0c0c;
  --term-surface: #141414;
  --term-surface-elevated: #1c1c1c;
  --term-surface-active: #242424;

  /* Text */
  --term-text: #e4e4e7;
  --term-text-muted: #71717a;
  --term-text-dim: #3f3f46;

  /* Semantic — the core of terminal color */
  --term-green: #4ade80;           /* Success, prompt, active */
  --term-red: #f87171;             /* Error, danger, exit code ≠ 0 */
  --term-yellow: #fbbf24;         /* Warning, caution */
  --term-blue: #60a5fa;           /* Info, links, references */
  --term-cyan: #22d3ee;           /* Paths, arguments */
  --term-magenta: #c084fc;        /* Special, keywords */
  --term-orange: #fb923c;         /* Numbers, values */
  --term-white: #e4e4e7;          /* Default text */

  /* Accent (choose one as primary) */
  --term-accent: var(--term-green);
  --term-accent-dim: rgba(74, 222, 128, 0.15);

  /* Borders */
  --term-border: #27272a;
  --term-border-active: #3f3f46;

  /* Selection */
  --term-selection: rgba(74, 222, 128, 0.2);
}
```

### Amber (Warm Alternative)
```css
:root {
  --term-accent: #f59e0b;
  --term-accent-dim: rgba(245, 158, 11, 0.15);
  --term-green: #f59e0b;  /* Amber replaces green as primary */
}
```

### Cyan (Cool Alternative)
```css
:root {
  --term-accent: #22d3ee;
  --term-accent-dim: rgba(34, 211, 238, 0.15);
}
```

### Catppuccin-Inspired (Softer)
```css
:root {
  --term-bg: #1e1e2e;
  --term-surface: #24243e;
  --term-text: #cdd6f4;
  --term-green: #a6e3a1;
  --term-red: #f38ba8;
  --term-yellow: #f9e2af;
  --term-blue: #89b4fa;
  --term-cyan: #94e2d5;
  --term-magenta: #cba6f7;
}
```

---

## Typography

### Monospace is King
```css
/* Primary — must support ligatures */
--font-mono: 'JetBrains Mono', monospace;
--font-mono-alt: 'Fira Code', monospace;

/* Alternative options */
--font-mono: 'Geist Mono', monospace;
--font-mono: 'Berkeley Mono', monospace;     /* Premium */
--font-mono: 'Monaspace Neon', monospace;    /* GitHub family */
--font-mono: 'Cascadia Code', monospace;     /* Microsoft */
--font-mono: 'Iosevka', monospace;           /* Narrow, dense */

/* Sans-serif — ONLY for marketing/landing hero text */
--font-sans: 'Geist', 'Inter', sans-serif;
```

### Type Scale
```css
/* Everything in monospace rhythm */
--text-hero: clamp(2.5rem, 6vw, 4rem);     /* Landing page only */
--text-h1: 1.5rem;                           /* Section headers */
--text-h2: 1.25rem;                          /* Sub-headers */
--text-h3: 1rem;                             /* Group labels */
--text-body: 0.875rem;                       /* Default terminal size */
--text-small: 0.8125rem;                     /* Secondary info */
--text-micro: 0.75rem;                       /* Status bar, metadata */

/* Tracking — monospace needs specific tuning */
--tracking-hero: -0.03em;                    /* Tighten hero only */
--tracking-body: 0;                          /* Never adjust mono tracking */

/* Line height — based on terminal line spacing */
--leading-code: 1.7;                         /* Code blocks */
--leading-body: 1.6;                         /* Prose */
--leading-compact: 1.4;                      /* Dense UI */

/* Ligatures */
font-feature-settings: "calt" 1, "liga" 1, "ss01" 1;
font-variant-ligatures: contextual;
```

### Advanced Typography
```css
/* Enable coding ligatures: => -> !== === */
code, pre, .mono {
  font-family: var(--font-mono);
  font-feature-settings: "calt" 1, "liga" 1;
  font-variant-ligatures: contextual;
  -webkit-font-smoothing: antialiased;
}

/* Tabular numbers for aligned data */
.tabular {
  font-variant-numeric: tabular-nums;
}
```

---

## Components

### Terminal Window
```css
.terminal {
  background: var(--term-bg);
  border: 1px solid var(--term-border);
  border-radius: 8px;
  overflow: hidden;
  font-family: var(--font-mono);
}

.terminal-titlebar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--term-surface);
  border-bottom: 1px solid var(--term-border);
  font-size: var(--text-micro);
  color: var(--term-text-muted);
}

.terminal-dots {
  display: flex;
  gap: 6px;
}
.terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.terminal-dot-red { background: #ef4444; }
.terminal-dot-yellow { background: #fbbf24; }
.terminal-dot-green { background: #4ade80; }

.terminal-body {
  padding: 16px;
  font-size: var(--text-body);
  line-height: var(--leading-code);
}

.terminal-line {
  display: flex;
  gap: 8px;
}

.prompt-symbol {
  color: var(--term-accent);
  user-select: none;
}
/* $ for bash, > for PS, % for zsh, λ for fancy */
```

### Command Palette / Search
```css
.command-palette {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 640px;
  background: var(--term-surface);
  border: 1px solid var(--term-border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
  z-index: 100;
}

.command-input {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--term-border);
  padding: 16px 20px;
  font-family: var(--font-mono);
  font-size: var(--text-body);
  color: var(--term-text);
}

.command-input::placeholder {
  color: var(--term-text-dim);
}

.command-results {
  max-height: 400px;
  overflow-y: auto;
}

.command-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  font-size: var(--text-body);
  color: var(--term-text-muted);
  cursor: pointer;
  transition: background 100ms;
}

.command-item:hover,
.command-item.active {
  background: var(--term-accent-dim);
  color: var(--term-text);
}

.command-shortcut {
  display: flex;
  gap: 4px;
}

.kbd {
  background: var(--term-surface-elevated);
  border: 1px solid var(--term-border);
  border-radius: 4px;
  padding: 2px 6px;
  font-family: var(--font-mono);
  font-size: var(--text-micro);
  color: var(--term-text-muted);
}
```

### Button
```css
/* Primary — accent colored */
.btn-primary {
  background: var(--term-accent-dim);
  color: var(--term-accent);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 6px;
  padding: 8px 16px;
  font-family: var(--font-mono);
  font-size: var(--text-small);
  cursor: pointer;
  transition: all 150ms;
}

.btn-primary:hover {
  background: rgba(74, 222, 128, 0.25);
  border-color: var(--term-accent);
}

/* Ghost */
.btn-ghost {
  background: transparent;
  color: var(--term-text-muted);
  border: 1px solid var(--term-border);
  border-radius: 6px;
  padding: 8px 16px;
  font-family: var(--font-mono);
  font-size: var(--text-small);
  transition: all 150ms;
}

.btn-ghost:hover {
  color: var(--term-text);
  border-color: var(--term-border-active);
  background: var(--term-surface);
}
```

### Card (Panel)
```css
.panel {
  background: var(--term-surface);
  border: 1px solid var(--term-border);
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--term-border);
  font-size: var(--text-small);
  color: var(--term-text-muted);
}

.panel-body {
  padding: 16px;
}

/* Status indicator in panel header */
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.status-dot.online { background: var(--term-green); }
.status-dot.error { background: var(--term-red); }
.status-dot.warning { background: var(--term-yellow); }
```

### Input
```css
.input {
  background: var(--term-bg);
  border: 1px solid var(--term-border);
  border-radius: 6px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: var(--text-body);
  color: var(--term-text);
  transition: border-color 150ms;
}

.input:focus {
  outline: none;
  border-color: var(--term-accent);
}
```

### Table (Data Grid)
```css
.data-table {
  width: 100%;
  font-family: var(--font-mono);
  font-size: var(--text-body);
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 8px 16px;
  color: var(--term-text-dim);
  font-weight: 500;
  font-size: var(--text-micro);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--term-border);
}

.data-table td {
  padding: 8px 16px;
  color: var(--term-text);
  border-bottom: 1px solid var(--term-border);
}

.data-table tr:hover td {
  background: var(--term-surface);
}

/* Semantic coloring in tables */
.data-table .status-ok { color: var(--term-green); }
.data-table .status-err { color: var(--term-red); }
.data-table .status-warn { color: var(--term-yellow); }
```

### Status Bar
```css
.statusbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 12px;
  background: var(--term-surface);
  border-top: 1px solid var(--term-border);
  font-family: var(--font-mono);
  font-size: var(--text-micro);
  color: var(--term-text-muted);
}

.statusbar-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.statusbar-separator {
  width: 1px;
  height: 14px;
  background: var(--term-border);
}
```

---

## Layout

### Principles
- **Information density first** — maximize data per viewport
- **Alignment to monospace grid** — every element snaps to character width
- **Sidebar + main + panel** — three-column IDE-like layout is native
- **Status bars** — top and bottom, always visible

### Dashboard Layout
```css
.layout-terminal {
  display: grid;
  grid-template-rows: 36px 1fr 24px;
  grid-template-columns: 240px 1fr 320px;
  height: 100vh;
  background: var(--term-bg);
  color: var(--term-text);
  font-family: var(--font-mono);
}

.layout-menubar { grid-column: 1 / -1; }
.layout-sidebar { border-right: 1px solid var(--term-border); }
.layout-main { overflow-y: auto; }
.layout-panel { border-left: 1px solid var(--term-border); }
.layout-statusbar { grid-column: 1 / -1; }

@media (max-width: 1024px) {
  .layout-terminal {
    grid-template-columns: 1fr;
  }
  .layout-sidebar,
  .layout-panel {
    display: none;
  }
}
```

---

## Animations

### Cursor Blink
```css
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.cursor {
  display: inline-block;
  width: 0.6em;
  height: 1.2em;
  background: var(--term-accent);
  animation: blink 1s step-end infinite;
  vertical-align: text-bottom;
}
```

### Typewriter Effect
```css
.typewriter {
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid var(--term-accent);
  animation:
    typing 2s steps(40) 1s forwards,
    blink-caret 0.75s step-end infinite;
  width: 0;
}

@keyframes typing {
  to { width: 100%; }
}

@keyframes blink-caret {
  50% { border-color: transparent; }
}
```

### Scan Line (Subtle)
```css
.scanlines::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 1px,
    rgba(0, 0, 0, 0.03) 1px,
    rgba(0, 0, 0, 0.03) 2px
  );
  pointer-events: none;
}
```

---

## Responsive Behavior

```css
/* Mobile: single column, hide panels */
@media (max-width: 768px) {
  .layout-terminal {
    grid-template-columns: 1fr;
    grid-template-rows: 36px 1fr 24px;
  }

  /* Increase touch targets */
  .btn-primary,
  .btn-ghost {
    padding: 12px 20px;
    font-size: var(--text-body);
  }

  .command-palette {
    top: 0;
    width: 100%;
    max-width: 100%;
    border-radius: 0;
  }
}
```

---

## Absolute Avoid List

- **Matrix rain / falling code** — overdone, cliche, not functional
- **Decorative fonts** — never mix serif or display fonts in. Monospace only (sans allowed for marketing hero ONLY)
- **Colorful backgrounds** — the background is black/near-black. Period.
- **Heavy shadows/elevation** — terminal elements are flat, separated by borders
- **Rounded-xl buttons** — max border-radius: 8px. This is a tool, not a toy
- **Gradient fills on UI elements** — gradients belong in Aurora, not here
- **Low information density** — if your terminal UI has less info per screen than an actual terminal, you failed
- **Ignoring semantic color** — green=ok, red=error, yellow=warn is non-negotiable

---

## Inspiration Keywords

Warp Terminal, Ghostty, Fig (now Amazon Q), Alacritty, WezTerm, Linear CLI, Charm.sh, Raycast, iTerm2, Hyper

---

## Final Check

> "If a senior engineer wouldn't use it daily, it's not terminal enough."
> "Density is not clutter. Clutter is bad organization. Density is efficient organization."
> "The best terminal UI makes you forget it's a web app."
