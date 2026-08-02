# Retro Pixel Style

## Core Philosophy
- The screen is a CRT monitor, every pixel is sacred
- Nostalgia is a design language, not a gimmick
- Constraints breed creativity: limited palettes, fixed grids
- The machine speaks through the interface
- Authenticity of early computing over modern polish

---

## Typography

Typography is your **terminal output**.

### Principles
- Monospace everything: every character occupies equal space
- Pixel-perfect rendering at fixed sizes
- All-caps for system headers and commands
- Blinking cursors and typewriter reveals
- Text is data, data is text

### Recommended Fonts
```css
/* Pixel fonts */
--font-pixel: 'Press Start 2P', cursive;
--font-pixel: 'Silkscreen', sans-serif;
--font-pixel: 'DotGothic16', sans-serif;

/* Terminal monospace */
--font-terminal: 'VT323', monospace;
--font-terminal: 'IBM Plex Mono', monospace;
--font-terminal: 'Share Tech Mono', monospace;

/* System monospace */
--font-system: 'JetBrains Mono', monospace;
--font-system: 'Fira Code', monospace;
--font-system: 'Source Code Pro', monospace;
```

### Type Scale
```css
--text-header: 2rem;      /* Main system header */
--text-title: 1.5rem;     /* Section titles */
--text-command: 1.125rem;  /* Command prompts */
--text-body: 1rem;         /* Standard terminal output */
--text-small: 0.875rem;    /* Status bar text */
--text-micro: 0.75rem;     /* System metadata */

/* Fixed character spacing */
--tracking-terminal: 0.05em;
--tracking-wide: 0.15em;
```

---

## Layout

### Principles
- Grid-based: everything snaps to a pixel grid
- Fixed-width containers emulating terminal columns (80-col standard)
- No fractional units: whole pixels only
- Bordered panels and windowed sections
- Content flows top-to-bottom like terminal output

### CSS Examples
```css
.pixel-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(8px, 1fr));
  gap: 0;
  image-rendering: pixelated;
}

/* 80-column terminal container */
.pixel-terminal {
  max-width: 80ch;
  margin: 0 auto;
  padding: 2rem;
  font-family: var(--font-terminal);
  line-height: 1.6;
}

/* Windowed panel (classic OS style) */
.pixel-window {
  border: 2px solid var(--color-text);
  background: var(--color-bg);
  position: relative;
}

.pixel-window-titlebar {
  background: var(--color-accent);
  color: var(--color-bg);
  padding: 4px 8px;
  font-size: var(--text-small);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--color-text);
}

.pixel-window-body {
  padding: 1rem;
}

/* Full screen CRT frame */
.pixel-screen {
  background: #0a0a0a;
  border-radius: 16px;
  padding: 2rem;
  box-shadow:
    inset 0 0 60px rgba(0, 0, 0, 0.8),
    0 0 20px rgba(0, 255, 0, 0.1);
  overflow: hidden;
  position: relative;
}
```

---

## Color

### Principles
- Limited palettes: 2-4 colors maximum per screen
- Phosphor glow colors: green, amber, or cool white
- Dark backgrounds are mandatory (the screen is off by default)
- Accent colors are bright and electric
- Color conveys system state: green = OK, red = error, yellow = warning

### Recommended Palettes
```css
/* Palette 1: Terminal Green (VT100) */
--color-bg: #0D0208;
--color-text: #00FF41;
--color-accent: #008F11;
--color-dim: #003B00;

/* Palette 2: Amber Monitor (IBM 5151) */
--color-bg: #1A0A00;
--color-text: #FFB000;
--color-accent: #FF8C00;
--color-dim: #4A2800;

/* Palette 3: Cool Phosphor (Monochrome) */
--color-bg: #0A0A0A;
--color-text: #B0B0B0;
--color-accent: #FFFFFF;
--color-dim: #404040;

/* Palette 4: Retro DOS (CGA-inspired) */
--color-bg: #000000;
--color-text: #AAAAAA;
--color-accent: #55FFFF;
--color-highlight: #FF55FF;
--color-warning: #FFFF55;
```

---

## Borders & Shapes

### Principles
- Borders are drawn with ASCII box-drawing characters or solid pixel lines
- No border-radius: everything is rectangular
- Double-line borders for emphasis
- Shadows are pixel-offset (no blur)
- Shapes are blocky, aliased, and deliberate

### CSS Examples
```css
.pixel-box {
  border: 2px solid var(--color-text);
  background: var(--color-bg);
  padding: 1rem;
}

.pixel-box-double {
  border: 4px double var(--color-text);
  background: var(--color-bg);
  padding: 1rem;
}

/* Pixel-offset shadow (no blur) */
.pixel-shadow {
  box-shadow: 4px 4px 0 var(--color-accent);
}

/* Inset terminal panel */
.pixel-inset {
  border: 2px solid var(--color-dim);
  border-top-color: var(--color-dim);
  border-left-color: var(--color-dim);
  border-bottom-color: var(--color-text);
  border-right-color: var(--color-text);
  background: #000000;
  padding: 1rem;
}

/* Raised button (3D pixel bevel) */
.pixel-raised {
  border: 2px solid var(--color-text);
  border-top-color: var(--color-accent);
  border-left-color: var(--color-accent);
  border-bottom-color: var(--color-dim);
  border-right-color: var(--color-dim);
  background: var(--color-bg);
  padding: 0.5rem 1rem;
}

/* Dashed terminal divider */
.pixel-divider {
  border: none;
  border-top: 2px dashed var(--color-dim);
  margin: 1.5rem 0;
}
```

---

## UI Components

### Principles
- Buttons look like keyboard keys or system commands
- Inputs emulate terminal prompts with blinking cursors
- Links are underlined or bracket-wrapped like [hyperlinks]
- Status indicators use ASCII characters and fixed-width labels
- All interactions feel like issuing commands

### CSS Examples
```css
/* Command button */
.pixel-button {
  font-family: var(--font-terminal);
  font-size: var(--text-body);
  border: 2px solid var(--color-text);
  background: var(--color-bg);
  color: var(--color-text);
  padding: 0.5rem 1.5rem;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  cursor: pointer;
  transition: none;
  position: relative;
}

.pixel-button:hover {
  background: var(--color-text);
  color: var(--color-bg);
}

.pixel-button:active {
  border-style: inset;
}

/* Prefix prompt marker */
.pixel-button::before {
  content: '> ';
}

/* Terminal input */
.pixel-input {
  font-family: var(--font-terminal);
  font-size: var(--text-body);
  border: 2px solid var(--color-dim);
  background: #000000;
  color: var(--color-text);
  padding: 0.5rem 1rem;
  width: 100%;
  caret-color: var(--color-text);
}

.pixel-input:focus {
  outline: none;
  border-color: var(--color-text);
  box-shadow: 0 0 8px var(--color-accent);
}

/* Prompt label */
.pixel-label {
  font-family: var(--font-terminal);
  color: var(--color-dim);
  text-transform: uppercase;
  font-size: var(--text-small);
  letter-spacing: var(--tracking-wide);
}

.pixel-label::after {
  content: ':~$';
  margin-left: 0.25em;
  color: var(--color-accent);
}

/* Bracket-wrapped link */
.pixel-link {
  color: var(--color-accent);
  text-decoration: none;
  font-family: var(--font-terminal);
}

.pixel-link::before {
  content: '[';
  color: var(--color-dim);
}

.pixel-link::after {
  content: ']';
  color: var(--color-dim);
}

.pixel-link:hover {
  color: var(--color-text);
  text-decoration: underline;
}

/* ASCII progress bar */
.pixel-progress {
  font-family: var(--font-terminal);
  color: var(--color-text);
  white-space: pre;
}
/* Render as: [=========>          ] 47% */

/* Status indicator */
.pixel-status {
  font-family: var(--font-terminal);
  font-size: var(--text-small);
}

.pixel-status::before {
  content: '[ OK ]';
  color: var(--color-accent);
  margin-right: 0.5rem;
}

.pixel-status--error::before {
  content: '[FAIL]';
  color: #FF0000;
}

.pixel-status--warn::before {
  content: '[WARN]';
  color: #FFB000;
}
```

---

## Interaction & Motion

### Principles
- Instant state changes, no smooth transitions
- Blinking and stepping animations only
- Typewriter text reveals character by character
- Cursor blink is the primary motion pattern
- Movement is discrete, never fluid

### CSS Examples
```css
/* Blinking cursor */
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.pixel-cursor::after {
  content: '\2588'; /* Full block character */
  animation: blink 1s step-end infinite;
  color: var(--color-text);
}

/* Typewriter text reveal */
@keyframes typewriter {
  from { width: 0; }
  to { width: 100%; }
}

.pixel-typewriter {
  overflow: hidden;
  white-space: nowrap;
  border-right: 0.15em solid var(--color-text);
  animation:
    typewriter 2s steps(40, end),
    blink 1s step-end infinite;
  font-family: var(--font-terminal);
}

/* Step transition (no easing) */
.pixel-step {
  transition: all 0s steps(1);
}

/* Flicker effect (CRT power-on) */
@keyframes flicker {
  0% { opacity: 0.1; }
  5% { opacity: 0.8; }
  10% { opacity: 0.2; }
  15% { opacity: 1; }
  20% { opacity: 0.6; }
  30% { opacity: 1; }
  100% { opacity: 1; }
}

.pixel-flicker {
  animation: flicker 0.5s ease-out;
}

/* Boot-up text sequence */
@keyframes boot {
  0% { opacity: 0; transform: translateY(4px); }
  100% { opacity: 1; transform: translateY(0); }
}

.pixel-boot > * {
  opacity: 0;
  animation: boot 0.1s steps(1) forwards;
}

.pixel-boot > *:nth-child(1) { animation-delay: 0.2s; }
.pixel-boot > *:nth-child(2) { animation-delay: 0.5s; }
.pixel-boot > *:nth-child(3) { animation-delay: 0.8s; }
.pixel-boot > *:nth-child(4) { animation-delay: 1.1s; }
.pixel-boot > *:nth-child(5) { animation-delay: 1.4s; }
```

---

## Textures & Effects

```css
/* CRT scanline overlay */
.pixel-scanlines::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    transparent,
    transparent 1px,
    rgba(0, 0, 0, 0.3) 1px,
    rgba(0, 0, 0, 0.3) 2px
  );
  pointer-events: none;
  z-index: 10;
}

/* CRT screen curvature and vignette */
.pixel-crt::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 60%,
    rgba(0, 0, 0, 0.6) 100%
  );
  pointer-events: none;
  z-index: 11;
}

/* Phosphor glow */
.pixel-glow {
  text-shadow:
    0 0 5px var(--color-accent),
    0 0 10px var(--color-accent),
    0 0 20px var(--color-dim);
}

/* RGB sub-pixel fringing */
.pixel-chromatic {
  text-shadow:
    -1px 0 rgba(255, 0, 0, 0.5),
    1px 0 rgba(0, 0, 255, 0.5);
}

/* Screen noise / static */
@keyframes noise {
  0%, 100% { background-position: 0 0; }
  10% { background-position: -5% -10%; }
  30% { background-position: 3% -15%; }
  50% { background-position: 12% 9%; }
  70% { background-position: -1% 4%; }
  90% { background-position: 7% -8%; }
}

.pixel-noise::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E");
  opacity: 0.15;
  pointer-events: none;
  animation: noise 0.5s steps(5) infinite;
  z-index: 12;
}

/* Pixel grid overlay */
.pixel-grid::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 4px 4px;
  pointer-events: none;
  z-index: 9;
}
```

---

## Absolute Avoid List

- Smooth gradients and soft transitions
- Rounded corners or pill shapes
- Anti-aliased decorative fonts
- Blur effects or glassmorphism
- Parallax scrolling
- Drop shadows with blur radius

---

## Inspiration Keywords

- CRT monitors and phosphor screens
- DOS command prompts and BIOS screens
- 8-bit and 16-bit game interfaces
- Early Macintosh System 1 through System 7
- VT100 terminal emulators
- BBS bulletin board systems
- Demoscene pixel art
- Retro computing and cyberpunk terminals

---

## Final Check

> If the screen flickers, the cursor blinks, and you instinctively want to type a command -- you have arrived.
> The machine is the medium. Every pixel is a deliberate act. This is computing at its most honest.
