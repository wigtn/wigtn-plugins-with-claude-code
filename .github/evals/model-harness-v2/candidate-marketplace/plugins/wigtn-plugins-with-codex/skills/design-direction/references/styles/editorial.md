# Editorial / Magazine Style

## Core Philosophy
- Less interface, more atmosphere
- Design should feel curated, not assembled
- Every visual decision must be intentional and restrained
- Premium, calm, and self-assured
- Never playful or loud

---

## Typography

Typography is the **protagonist** of your design.

### Principles
- Use large, expressive headlines
- Allow generous vertical space for headlines
- Strong contrast between headlines and body text
- Prefer serif or elegant sans-serif
- No rounded or decorative fonts

### Recommended Font Pairings
```css
/* Pairing 1: Classic Editorial */
--font-headline: 'Playfair Display', serif;
--font-body: 'Source Sans 3', sans-serif;

/* Pairing 2: Modern Fashion */
--font-headline: 'Cormorant Garamond', serif;
--font-body: 'Jost', sans-serif;

/* Pairing 3: Luxury Magazine */
--font-headline: 'Bodoni Moda', serif;
--font-body: 'Lato', sans-serif;

/* Pairing 4: Minimal Editorial */
--font-headline: 'PP Editorial New', serif;
--font-body: 'Inter', sans-serif; /* Acceptable for body */
```

### Type Scale
```css
--text-hero: clamp(3rem, 8vw, 7rem);      /* Main headline */
--text-title: clamp(2rem, 5vw, 4rem);      /* Section titles */
--text-subtitle: clamp(1.25rem, 2vw, 1.5rem);
--text-body: 1rem;
--text-small: 0.875rem;
--text-caption: 0.75rem;

/* Letter spacing */
--tracking-tight: -0.02em;    /* Large headlines */
--tracking-wide: 0.1em;       /* Small captions, labels */
```

---

## Layout

### Principles
- Mobile-first
- Allow intentional asymmetry and broken grids
- Do not force perfect visual balance
- Embrace editorial tension and negative space
- Whitespace is a feature, not empty space
- Components should feel unboxed and breathable

### CSS Examples
```css
.editorial-layout {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100%) 1fr;
  padding-block: clamp(4rem, 10vh, 8rem);
}

.editorial-hero {
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding-bottom: 15vh;
}

/* Intentional offset */
.offset-left { margin-left: -5vw; }
.offset-right { margin-right: -5vw; }

/* Overlap */
.overlap-up { margin-top: -10vh; }
```

---

## Imagery

### Principles
- Imagery is the primary storytelling element
- Prefer candid, lifestyle-oriented photography
- Avoid stock-photo aesthetics
- Edge-to-edge imagery is encouraged
- Text may overlap images if it enhances mood and hierarchy

### CSS Examples
```css
.editorial-image {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  height: 80vh;
  object-fit: cover;
}

.image-with-text-overlay {
  position: relative;
}

.image-with-text-overlay h2 {
  position: absolute;
  bottom: 2rem;
  left: 2rem;
  color: white;
  mix-blend-mode: difference;
}
```

---

## Color

### Principles
- Base palette should be monochrome or near-monochrome
- Use only one accent color, sparingly and intentionally
- Avoid gradients unless explicitly requested

### Recommended Palettes
```css
/* Palette 1: Classic B&W */
--color-bg: #FAFAFA;
--color-surface: #FFFFFF;
--color-text: #1A1A1A;
--color-text-muted: #666666;
--color-accent: #C9A227;  /* Gold accent */

/* Palette 2: Warm Neutrals */
--color-bg: #F5F3EF;
--color-surface: #FFFFFF;
--color-text: #2C2C2C;
--color-text-muted: #8B8680;
--color-accent: #B8860B;

/* Palette 3: Dark Mode Editorial */
--color-bg: #0A0A0A;
--color-surface: #141414;
--color-text: #F5F5F5;
--color-text-muted: #888888;
--color-accent: #E8D5B7;
```

---

## UI Components

### Principles
- Buttons should be flat, minimal, and confident
- Avoid heavy borders, outlines, or containers
- Reduce visual affordances; trust user intuition
- Icons should be minimal or omitted if unnecessary
- Prefer text-based actions over icon-driven controls

### CSS Examples
```css
.editorial-button {
  background: transparent;
  border: none;
  border-bottom: 1px solid currentColor;
  padding: 0.5rem 0;
  font-size: 0.875rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.editorial-button:hover {
  opacity: 0.6;
}

/* Or minimal solid */
.editorial-button-solid {
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  padding: 1rem 2rem;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}
```

---

## Interaction & Motion

### Principles
- Motion must be subtle and intentional
- Allowed motions:
  - Opacity transitions
  - Slight translate
  - Scale ≤ 1.05
- No bounce, spring, or playful easing
- Interactions should feel editorial and composed, not "app-like"

### CSS Examples
```css
.editorial-fade-in {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeIn 0.8s ease-out forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Staggered reveal */
.editorial-stagger > * {
  opacity: 0;
  animation: fadeIn 0.6s ease-out forwards;
}
.editorial-stagger > *:nth-child(1) { animation-delay: 0.1s; }
.editorial-stagger > *:nth-child(2) { animation-delay: 0.2s; }
.editorial-stagger > *:nth-child(3) { animation-delay: 0.3s; }

/* Hover */
.editorial-link:hover {
  opacity: 0.6;
  transition: opacity 0.3s ease;
}
```

---

## Absolute Avoid List

- Cute, playful, or gamified UI
- Overuse of cards or boxed components
- Bright, neon, or saturated color palettes
- Decorative icons, emojis, or stickers
- Trend-driven effects without editorial justification

---

## Final Check

> Every screen should feel like a page from a modern fashion magazine,
> translated into a digital product with restraint and confidence.
