# Swiss Minimal / International Style

## Core Philosophy
- Form follows function
- The grid is sacred
- Typography is design
- Less is more, but details matter
- Timeless elegance

---

## Historical Background

The Swiss Style (International Typographic Style) began in Switzerland in the 1950s and remains one of the most influential design languages to this day.

Key figures: Max Miedinger (Helvetica designer), Josef Müller-Brockmann, Emil Ruder

---

## Grid System

### Principles
- Everything aligns to the grid
- Mathematical proportions and rhythm
- Margins are part of the grid
- Modular system

### CSS Examples
```css
/* 12-column grid */
.swiss-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--grid-gap, 1.5rem);
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--grid-margin, 2rem);
}

/* Modular scale */
:root {
  --space-unit: 8px;
  --space-xs: calc(var(--space-unit) * 1);   /* 8px */
  --space-sm: calc(var(--space-unit) * 2);   /* 16px */
  --space-md: calc(var(--space-unit) * 3);   /* 24px */
  --space-lg: calc(var(--space-unit) * 4);   /* 32px */
  --space-xl: calc(var(--space-unit) * 6);   /* 48px */
  --space-2xl: calc(var(--space-unit) * 8);  /* 64px */
  --space-3xl: calc(var(--space-unit) * 12); /* 96px */
}

/* Section spacing */
.swiss-section {
  padding-block: var(--space-3xl);
}
```

---

## Typography

### Principles
- Sans-serif is default
- Clear hierarchy
- Attention to letter-spacing and line-height
- Left-aligned (rag right)
- Structure through contrast

### Recommended Fonts
```css
/* Classic */
--font-primary: 'Helvetica Neue', Helvetica, Arial, sans-serif;

/* Modern interpretations */
--font-primary: 'Neue Haas Grotesk', sans-serif;
--font-primary: 'Suisse Int\'l', sans-serif;
--font-primary: 'Akkurat', sans-serif;
--font-primary: 'GT America', sans-serif;

/* Accessible alternatives (Google Fonts) */
--font-primary: 'Inter', sans-serif;
--font-primary: 'DM Sans', sans-serif;
--font-primary: 'Manrope', sans-serif;
```

### Type Scale
```css
/* Modular scale (1.25 ratio) */
--text-xs: 0.64rem;      /* 10.24px */
--text-sm: 0.8rem;       /* 12.8px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.25rem;      /* 20px */
--text-xl: 1.563rem;     /* 25px */
--text-2xl: 1.953rem;    /* 31.25px */
--text-3xl: 2.441rem;    /* 39px */
--text-4xl: 3.052rem;    /* 48.8px */
--text-5xl: 3.815rem;    /* 61px */

/* Line height */
--leading-tight: 1.1;
--leading-snug: 1.3;
--leading-normal: 1.5;
--leading-relaxed: 1.7;

/* Letter spacing */
--tracking-tight: -0.02em;
--tracking-normal: 0;
--tracking-wide: 0.05em;
```

### Typography Styles
```css
.swiss-headline {
  font-size: var(--text-4xl);
  font-weight: 700;
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text);
}

.swiss-subhead {
  font-size: var(--text-lg);
  font-weight: 400;
  line-height: var(--leading-snug);
  color: var(--color-text-secondary);
}

.swiss-body {
  font-size: var(--text-base);
  font-weight: 400;
  line-height: var(--leading-relaxed);
  max-width: 65ch; /* Optimal line length */
}

.swiss-caption {
  font-size: var(--text-sm);
  font-weight: 500;
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}
```

---

## Color

### Principles
- Limited palette
- Black and white as base
- Single accent, used functionally
- Color serves information delivery

### Recommended Palettes
```css
/* Classic B&W */
:root {
  --color-bg: #FFFFFF;
  --color-surface: #FAFAFA;
  --color-text: #0A0A0A;
  --color-text-secondary: #525252;
  --color-text-tertiary: #A3A3A3;
  --color-border: #E5E5E5;
  --color-accent: #0066FF; /* Functional accent */
}

/* Dark mode */
:root.dark {
  --color-bg: #0A0A0A;
  --color-surface: #141414;
  --color-text: #FAFAFA;
  --color-text-secondary: #A3A3A3;
  --color-text-tertiary: #525252;
  --color-border: #262626;
  --color-accent: #3B82F6;
}

/* Single accent usage */
.swiss-link {
  color: var(--color-accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s ease;
}

.swiss-link:hover {
  border-bottom-color: var(--color-accent);
}
```

---

## Layout Patterns

### Principles
- Asymmetric balance
- Left-aligned focus
- Space division through whitespace
- Clear information hierarchy

### CSS Examples
```css
/* Classic 2/3 layout */
.swiss-split {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-xl);
  align-items: start;
}

/* Asymmetric hero */
.swiss-hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-2xl);
  padding-block: var(--space-3xl);
}

/* Index layout */
.swiss-index {
  display: grid;
  grid-template-columns: minmax(100px, 200px) 1fr;
  gap: var(--space-lg);
  border-top: 1px solid var(--color-border);
  padding-block: var(--space-lg);
}
```

---

## Components

### Buttons
```css
/* Minimal button */
.swiss-button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--text-sm);
  font-weight: 500;
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  background: var(--color-text);
  color: var(--color-bg);
  border: none;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.swiss-button:hover {
  opacity: 0.85;
}

/* Ghost button */
.swiss-button-ghost {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-text);
}

.swiss-button-ghost:hover {
  background: var(--color-text);
  color: var(--color-bg);
}
```

### Cards
```css
.swiss-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-lg);
  background: var(--color-surface);
}

/* Outlined variant */
.swiss-card-outlined {
  background: transparent;
  border: 1px solid var(--color-border);
}
```

### Dividers
```css
.swiss-divider {
  height: 1px;
  background: var(--color-border);
  border: none;
  margin-block: var(--space-xl);
}

.swiss-divider-thick {
  height: 2px;
  background: var(--color-text);
}
```

---

## Navigation

```css
.swiss-nav {
  display: flex;
  gap: var(--space-xl);
  padding-block: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}

.swiss-nav-item {
  font-size: var(--text-sm);
  font-weight: 500;
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.swiss-nav-item:hover,
.swiss-nav-item.active {
  color: var(--color-text);
}

/* Numbered index style */
.swiss-nav-numbered {
  counter-reset: nav;
}

.swiss-nav-numbered .swiss-nav-item::before {
  counter-increment: nav;
  content: counter(nav, decimal-leading-zero);
  margin-right: var(--space-xs);
  color: var(--color-text-tertiary);
}
```

---

## Animation

### Principles
- Motion is minimal or very subtle
- Use only ease-out curves
- Around 200-300ms
- Focus on content

```css
/* Page transition */
.swiss-page-enter {
  opacity: 0;
  transform: translateY(20px);
  animation: swissFadeIn 0.4s ease-out forwards;
}

@keyframes swissFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover effect */
.swiss-hover {
  transition: opacity 0.2s ease-out;
}

.swiss-hover:hover {
  opacity: 0.7;
}
```

---

## Image Treatment

```css
/* Images always fit the grid */
.swiss-image {
  width: 100%;
  aspect-ratio: 4/3;
  object-fit: cover;
}

/* Captions */
.swiss-figure {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.swiss-figcaption {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}
```

---

## Absolute Avoid List

- Gradients (without special reason)
- Excessive shadows
- Rounded corners (even small values)
- Decorative elements
- Elements outside the grid
- Too many colors

---

## Inspiration Sources

- Swiss Poster Design
- Dieter Rams' Braun products
- Kinfolk Magazine
- Monocle
- Apple (early Jony Ive era)

---

## Final Check

> Swiss style pursues "invisible design."
> If users focus on content without noticing the design, you've succeeded.
> Every pixel must have a purpose.
