# Neobrutalism Style Guide

## Core Philosophy
- Bold, playful, unapologetically loud
- Thick borders are the signature, not the accent
- Color is maximalist — pastels meet vivid primaries
- Friendly chaos, not hostile destruction
- Handmade, zine-culture energy meets modern web

---

## Core Characteristics

| Aspect | Description |
|--------|-------------|
| Feel | Playful, bold, energetic, approachable |
| Borders | Thick black outlines (2-4px), always visible |
| Shadows | Hard offset shadows (no blur), solid color |
| Colors | Vivid pastels + bright primaries, high saturation |
| Corners | Mixed — sharp OR chunky rounded (8-16px), never subtle |
| Typography | Bold, chunky, often slightly quirky |

---

## Neobrutalism vs Brutalism

| | Brutalism | Neobrutalism |
|--|-----------|-------------|
| Mood | Hostile, uncomfortable | Friendly, playful |
| Color | Monochrome, raw primary | Pastel + vivid, harmonious chaos |
| Border | Thick, aggressive | Thick, decorative |
| Shadow | Hard, ominous | Hard, colorful, bouncy |
| Layout | Broken grids, overlap | Structured but unexpected |
| Audience | Art/design-savvy | Everyone, especially Gen Z |

---

## Color Palette

### Primary Palette (Mix & Match)
```css
:root {
  /* Vivid pastels — the signature */
  --neo-yellow: #FFD803;
  --neo-pink: #FF6B9D;
  --neo-blue: #80B3FF;
  --neo-green: #7AE582;
  --neo-purple: #C4B5FD;
  --neo-orange: #FFAC33;
  --neo-peach: #FFCBA4;
  --neo-mint: #98F5E1;

  /* Structural */
  --neo-black: #1A1A2E;
  --neo-white: #FFFDF7;
  --neo-bg: #FFFDF7;

  /* Text */
  --neo-text: #1A1A2E;
  --neo-text-muted: #4A4A5E;
}
```

### Palette Combos
```css
/* Combo 1: Sunshine Zine */
--neo-primary: #FFD803;
--neo-secondary: #FF6B9D;
--neo-accent: #80B3FF;
--neo-bg: #FFFDF7;

/* Combo 2: Candy Shop */
--neo-primary: #FF6B9D;
--neo-secondary: #C4B5FD;
--neo-accent: #7AE582;
--neo-bg: #FFF5F7;

/* Combo 3: Ocean Breeze */
--neo-primary: #80B3FF;
--neo-secondary: #98F5E1;
--neo-accent: #FFD803;
--neo-bg: #F0F8FF;

/* Combo 4: Forest Party */
--neo-primary: #7AE582;
--neo-secondary: #FFD803;
--neo-accent: #FF6B9D;
--neo-bg: #F0FFF4;
```

---

## Typography

### Principles
- Headlines are CHUNKY and demand attention
- Mix weights aggressively (900 + 400)
- Slight quirkiness in font choice (not generic)
- ALL CAPS for labels and badges, mixed case for body

### Recommended Fonts
```css
/* Headlines — chunky and bold */
--font-heading: 'Space Grotesk', sans-serif;
--font-heading: 'DM Sans', sans-serif;
--font-heading: 'Sora', sans-serif;
--font-heading: 'Clash Display', sans-serif;

/* Body — clean but with character */
--font-body: 'Inter', sans-serif;
--font-body: 'Plus Jakarta Sans', sans-serif;

/* Accent — for labels, badges */
--font-accent: 'Space Mono', monospace;
--font-accent: 'JetBrains Mono', monospace;
```

### Type Scale
```css
--text-mega: clamp(3rem, 8vw, 6rem);
--text-hero: clamp(2rem, 5vw, 4rem);
--text-title: clamp(1.5rem, 3vw, 2.5rem);
--text-subtitle: 1.25rem;
--text-body: 1rem;
--text-small: 0.875rem;
--text-badge: 0.75rem;

/* Weight pairing */
--weight-headline: 800;
--weight-body: 400;
--weight-bold: 700;
```

### Text Styles
```css
.neo-heading {
  font-family: var(--font-heading);
  font-weight: 800;
  color: var(--neo-text);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.neo-badge-text {
  font-family: var(--font-accent);
  font-size: var(--text-badge);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

---

## The Border System (Core Identity)

### Principles
- **Every interactive element gets a black border**
- Border width: 2px (subtle) to 4px (bold) — never 1px
- Borders are structural, not decorative
- Even images and illustrations get bordered

```css
/* Standard border */
.neo-border {
  border: 3px solid var(--neo-black);
}

/* Thick border (cards, primary elements) */
.neo-border-thick {
  border: 4px solid var(--neo-black);
}

/* Subtle border (secondary elements) */
.neo-border-thin {
  border: 2px solid var(--neo-black);
}
```

---

## Shadow System (Hard Offset)

### Principles
- **No blur ever** — shadows are solid blocks
- Shadows go bottom-right (consistent direction)
- Shadow color matches border color (usually black)
- Shadow size: 4-8px offset

```css
/* Standard shadow */
.neo-shadow {
  box-shadow: 4px 4px 0 var(--neo-black);
}

/* Large shadow (hero elements) */
.neo-shadow-lg {
  box-shadow: 6px 6px 0 var(--neo-black);
}

/* Extra large shadow */
.neo-shadow-xl {
  box-shadow: 8px 8px 0 var(--neo-black);
}

/* Colored shadow (playful variant) */
.neo-shadow-pink {
  box-shadow: 4px 4px 0 var(--neo-pink);
}

.neo-shadow-blue {
  box-shadow: 4px 4px 0 var(--neo-blue);
}

/* Hover: shadow grows, element lifts */
.neo-hover {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.neo-hover:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--neo-black);
}

/* Active: shadow shrinks, element presses */
.neo-hover:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 var(--neo-black);
}
```

---

## UI Components

### Button
```css
.neo-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1rem;
  color: var(--neo-black);
  background: var(--neo-yellow);
  border: 3px solid var(--neo-black);
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 4px 4px 0 var(--neo-black);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.neo-button:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--neo-black);
}

.neo-button:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 var(--neo-black);
}

/* Variants */
.neo-button-pink { background: var(--neo-pink); }
.neo-button-blue { background: var(--neo-blue); }
.neo-button-green { background: var(--neo-green); }

/* Outline variant */
.neo-button-outline {
  background: var(--neo-white);
}

.neo-button-outline:hover {
  background: var(--neo-yellow);
}
```

### Card
```css
.neo-card {
  background: var(--neo-white);
  border: 3px solid var(--neo-black);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 6px 6px 0 var(--neo-black);
}

/* Colored card */
.neo-card-yellow { background: var(--neo-yellow); }
.neo-card-pink { background: var(--neo-pink); }
.neo-card-blue { background: var(--neo-blue); }
.neo-card-green { background: var(--neo-green); }

/* Card with image */
.neo-card-image {
  overflow: hidden;
  padding: 0;
}

.neo-card-image img {
  width: 100%;
  display: block;
  border-bottom: 3px solid var(--neo-black);
}

.neo-card-image-body {
  padding: 20px;
}
```

### Input
```css
.neo-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  color: var(--neo-text);
  background: var(--neo-white);
  border: 3px solid var(--neo-black);
  border-radius: 12px;
  box-shadow: 3px 3px 0 var(--neo-black);
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.neo-input:focus {
  outline: none;
  background: #FFFFF0;
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0 var(--neo-black);
}

.neo-input::placeholder {
  color: var(--neo-text-muted);
}
```

### Badge / Tag
```css
.neo-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  font-family: var(--font-accent);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--neo-black);
  background: var(--neo-yellow);
  border: 2px solid var(--neo-black);
  border-radius: 8px;
  box-shadow: 2px 2px 0 var(--neo-black);
}

.neo-badge-pink { background: var(--neo-pink); }
.neo-badge-blue { background: var(--neo-blue); }
.neo-badge-green { background: var(--neo-green); }
```

### Toggle
```css
.neo-toggle {
  width: 56px;
  height: 30px;
  background: var(--neo-white);
  border: 3px solid var(--neo-black);
  border-radius: 15px;
  position: relative;
  cursor: pointer;
  transition: background 0.2s ease;
}

.neo-toggle::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  background: var(--neo-black);
  border-radius: 50%;
  transition: transform 0.2s ease;
}

.neo-toggle.active {
  background: var(--neo-green);
}

.neo-toggle.active::after {
  transform: translateX(26px);
}
```

### Avatar
```css
.neo-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 3px solid var(--neo-black);
  box-shadow: 3px 3px 0 var(--neo-black);
  object-fit: cover;
}

/* Avatar group with overlap */
.neo-avatar-group {
  display: flex;
}

.neo-avatar-group .neo-avatar + .neo-avatar {
  margin-left: -12px;
}
```

---

## Layout

### Principles
- Grid-based but with personality
- Mix card sizes for visual interest
- Use color blocks to create sections
- White space is generous but intentional

```css
/* Asymmetric grid */
.neo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

/* Featured layout (1 big + 2 small) */
.neo-grid-featured {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: 24px;
}

.neo-grid-featured > :first-child {
  grid-row: 1 / 3;
}

/* Section with color background */
.neo-section {
  padding: 4rem 2rem;
}

.neo-section-yellow { background: var(--neo-yellow); }
.neo-section-pink { background: var(--neo-pink); }

/* Marquee / Ticker */
.neo-marquee {
  overflow: hidden;
  border-top: 3px solid var(--neo-black);
  border-bottom: 3px solid var(--neo-black);
  padding: 12px 0;
  background: var(--neo-yellow);
}

.neo-marquee-content {
  display: inline-flex;
  gap: 3rem;
  animation: neoMarquee 20s linear infinite;
  font-weight: 800;
  font-size: 1.25rem;
  text-transform: uppercase;
  white-space: nowrap;
}

@keyframes neoMarquee {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
```

---

## Interaction & Motion

### Principles
- Snappy, not smooth — quick transitions (0.1-0.2s)
- Translate on hover (lift up-left), translate on press (push down-right)
- Slight rotation or scale for playfulness
- No elastic/spring physics — keep it crisp

```css
/* Standard hover */
.neo-interactive {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.neo-interactive:hover {
  transform: translate(-2px, -2px);
}

.neo-interactive:active {
  transform: translate(2px, 2px);
}

/* Wiggle on hover (playful) */
.neo-wiggle:hover {
  animation: neoWiggle 0.3s ease;
}

@keyframes neoWiggle {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-2deg); }
  75% { transform: rotate(2deg); }
}

/* Pop-in animation */
.neo-pop-in {
  animation: neoPopIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes neoPopIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Stagger children */
.neo-stagger > * {
  animation: neoPopIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) backwards;
}

.neo-stagger > *:nth-child(1) { animation-delay: 0ms; }
.neo-stagger > *:nth-child(2) { animation-delay: 80ms; }
.neo-stagger > *:nth-child(3) { animation-delay: 160ms; }
.neo-stagger > *:nth-child(4) { animation-delay: 240ms; }
```

---

## Illustrations & Decorations

```css
/* Decorative sticker */
.neo-sticker {
  display: inline-block;
  padding: 8px 16px;
  background: var(--neo-pink);
  border: 2px solid var(--neo-black);
  border-radius: 20px;
  transform: rotate(-3deg);
  box-shadow: 3px 3px 0 var(--neo-black);
  font-weight: 700;
}

/* Doodle underline */
.neo-underline {
  position: relative;
}

.neo-underline::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -4px;
  width: 100%;
  height: 4px;
  background: var(--neo-yellow);
  border-radius: 2px;
}

/* Highlight marker effect */
.neo-highlight {
  background: linear-gradient(transparent 60%, var(--neo-yellow) 60%);
  padding: 0 4px;
}
```

---

## Absolute Avoid List

- Blur shadows (the #1 rule: no blur, ever)
- 1px borders (too subtle — minimum 2px)
- Subtle/muted colors (this isn't minimalism)
- Smooth, slow animations (keep it snappy)
- Dark, moody palettes (neobrutalism is cheerful)
- Gradient borders or gradient shadows
- Overthinking it — neobrutalism is fun, not precious

---

## Inspiration Keywords

- Gumroad redesign
- Indie SaaS landing pages
- Zine culture meets modern web
- Pop art meets UI design
- Notion-style playfulness
- Figma community templates
- Gen Z aesthetic

---

## Final Check

> If it doesn't make you smile, it's not neobrutalist enough.
> Every element should have a visible border. Every interactive element should have a hard shadow.
> The palette should feel like a candy store — vivid, cheerful, unapologetic.
