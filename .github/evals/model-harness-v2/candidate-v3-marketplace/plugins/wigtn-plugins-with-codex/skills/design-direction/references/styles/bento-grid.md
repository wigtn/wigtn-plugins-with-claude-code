# Bento Grid Style Guide

## Overview
Bento Grid is inspired by Japanese bento boxes and Apple's design language. It features modular cards of varying sizes arranged in a grid, creating visual interest through size contrast and strategic content placement.

---

## Core Characteristics

| Aspect | Description |
|--------|-------------|
| Feel | Modern, organized, visually rich |
| Layout | Modular grid with varied card sizes |
| Colors | Neutral base with vibrant accent cards |
| Borders | None or subtle, rounded corners |
| Spacing | Consistent gaps, generous padding |

---

## Color Palette

### Light Mode
```css
:root {
  --background: #ffffff;
  --foreground: #1d1d1f;
  --card-default: #f5f5f7;
  --card-accent-1: #fef2f2;    /* Soft red */
  --card-accent-2: #eff6ff;    /* Soft blue */
  --card-accent-3: #f0fdf4;    /* Soft green */
  --card-accent-4: #faf5ff;    /* Soft purple */
  --card-dark: #1d1d1f;        /* Dark feature card */
  --muted: #86868b;
  --border: #d2d2d7;
}
```

### Dark Mode
```css
.dark {
  --background: #000000;
  --foreground: #f5f5f7;
  --card-default: #1d1d1f;
  --card-accent-1: #2d1f1f;
  --card-accent-2: #1f2937;
  --card-accent-3: #1f2d1f;
  --card-accent-4: #2d1f3d;
  --card-dark: #f5f5f7;
  --muted: #86868b;
  --border: #424245;
}
```

---

## Typography

### Recommended Fonts
- **Primary**: SF Pro Display, Geist, Inter
- **Headlines**: SF Pro Display (bold weight)

### Hierarchy
```css
/* Large feature headline */
.headline-large {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

/* Card headline */
.headline-card {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

/* Eyebrow/Label */
.eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
}

/* Body text */
.body {
  font-size: 1rem;
  line-height: 1.5;
  color: var(--muted);
}
```

---

## Grid System

### Basic Grid
```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
}
```

### Card Sizes
```css
/* 1x1 - Small square */
.bento-1x1 {
  grid-column: span 1;
  grid-row: span 1;
  aspect-ratio: 1;
}

/* 2x1 - Wide rectangle */
.bento-2x1 {
  grid-column: span 2;
  grid-row: span 1;
}

/* 1x2 - Tall rectangle */
.bento-1x2 {
  grid-column: span 1;
  grid-row: span 2;
}

/* 2x2 - Large square */
.bento-2x2 {
  grid-column: span 2;
  grid-row: span 2;
}

/* Full width */
.bento-full {
  grid-column: 1 / -1;
}
```

### Layout Example
```html
<div class="bento-grid">
  <div class="bento-card bento-2x2">Feature</div>
  <div class="bento-card bento-1x1">Small 1</div>
  <div class="bento-card bento-1x1">Small 2</div>
  <div class="bento-card bento-2x1">Wide</div>
  <div class="bento-card bento-1x2">Tall</div>
  <div class="bento-card bento-1x1">Small 3</div>
  <div class="bento-card bento-2x1">Wide 2</div>
</div>
```

---

## Card Components

### Base Card
```css
.bento-card {
  background: var(--card-default);
  border-radius: 24px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  transition: transform 300ms ease, box-shadow 300ms ease;
}

.bento-card:hover {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
```

### Feature Card (Dark)
```css
.bento-card-dark {
  background: var(--card-dark);
  color: white;
}

.bento-card-dark .eyebrow {
  color: rgba(255, 255, 255, 0.6);
}

.bento-card-dark .body {
  color: rgba(255, 255, 255, 0.7);
}
```

### Accent Cards
```css
.bento-card-red { background: var(--card-accent-1); }
.bento-card-blue { background: var(--card-accent-2); }
.bento-card-green { background: var(--card-accent-3); }
.bento-card-purple { background: var(--card-accent-4); }
```

### Card with Image
```css
.bento-card-image {
  padding: 0;
  position: relative;
}

.bento-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bento-card-image .content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: white;
}
```

### Card with Icon
```css
.bento-card-icon {
  align-items: center;
  justify-content: center;
  text-align: center;
}

.bento-card-icon .icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.bento-card-icon .headline-card {
  margin-bottom: 8px;
}
```

---

## Content Patterns

### Stats Card
```html
<div class="bento-card bento-1x1">
  <span class="eyebrow">Active Users</span>
  <div class="stat-value">2.4M</div>
  <span class="stat-change positive">+12.5%</span>
</div>
```

```css
.stat-value {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.stat-change {
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-change.positive { color: #22c55e; }
.stat-change.negative { color: #ef4444; }
```

### Feature Highlight
```html
<div class="bento-card bento-2x2 bento-card-dark">
  <div>
    <span class="eyebrow">New Feature</span>
    <h2 class="headline-large">AI-Powered Analytics</h2>
  </div>
  <p class="body">Get intelligent insights from your data automatically.</p>
  <img src="feature-visual.png" alt="" class="feature-image" />
</div>
```

### Icon Grid Card
```html
<div class="bento-card bento-2x1">
  <span class="eyebrow">Integrations</span>
  <div class="icon-grid">
    <img src="slack.svg" alt="Slack" />
    <img src="notion.svg" alt="Notion" />
    <img src="figma.svg" alt="Figma" />
    <img src="github.svg" alt="GitHub" />
  </div>
</div>
```

---

## Animations

### Card Entrance
```css
.bento-card {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 600ms ease forwards;
}

.bento-card:nth-child(1) { animation-delay: 0ms; }
.bento-card:nth-child(2) { animation-delay: 100ms; }
.bento-card:nth-child(3) { animation-delay: 200ms; }
.bento-card:nth-child(4) { animation-delay: 300ms; }
/* Continue pattern... */

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Hover Effects
```css
/* Scale up */
.bento-card:hover {
  transform: scale(1.02);
}

/* Lift */
.bento-card-lift:hover {
  transform: translateY(-8px);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.15);
}

/* Glow (for dark cards) */
.bento-card-dark:hover {
  box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
}
```

---

## Responsive Behavior

```css
.bento-grid {
  display: grid;
  gap: 16px;
}

/* Desktop: 4 columns */
@media (min-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Tablet: 2 columns, preserve large cards */
@media (min-width: 640px) and (max-width: 1023px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bento-2x2 {
    grid-column: span 2;
    grid-row: span 2;
  }
}

/* Mobile: Stack */
@media (max-width: 639px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }

  .bento-1x1,
  .bento-2x1,
  .bento-1x2,
  .bento-2x2 {
    grid-column: span 1;
    grid-row: span 1;
    aspect-ratio: auto;
    min-height: 200px;
  }

  /* Feature cards stay larger */
  .bento-2x2 {
    min-height: 300px;
  }
}
```

---

## Tailwind Classes

```html
<!-- Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

  <!-- 2x2 Feature Card -->
  <div class="md:col-span-2 md:row-span-2 bg-zinc-900 text-white rounded-3xl p-6">
    ...
  </div>

  <!-- 1x1 Card -->
  <div class="bg-zinc-100 rounded-3xl p-6 aspect-square">
    ...
  </div>

  <!-- 2x1 Wide Card -->
  <div class="md:col-span-2 bg-blue-50 rounded-3xl p-6">
    ...
  </div>

</div>
```

---

## Do's and Don'ts

### ✅ Do
- Vary card sizes for visual interest
- Use a feature card (2x2 or full width) as focal point
- Keep consistent padding and gap
- Use subtle background colors for variety
- Add hover animations for interactivity

### ❌ Don't
- Make all cards the same size
- Overcrowd cards with content
- Use too many accent colors (2-3 max)
- Forget mobile responsiveness
- Skip the rounded corners (they're essential)
