# Spacing & Density Systems

## Overview
This module provides spacing scales and density configurations for different layout preferences.

---

## Base Spacing Scale

Use a consistent 4px base unit:

```css
:root {
  --space-0: 0;
  --space-1: 4px;    /* 0.25rem */
  --space-2: 8px;    /* 0.5rem */
  --space-3: 12px;   /* 0.75rem */
  --space-4: 16px;   /* 1rem */
  --space-5: 20px;   /* 1.25rem */
  --space-6: 24px;   /* 1.5rem */
  --space-8: 32px;   /* 2rem */
  --space-10: 40px;  /* 2.5rem */
  --space-12: 48px;  /* 3rem */
  --space-16: 64px;  /* 4rem */
  --space-20: 80px;  /* 5rem */
  --space-24: 96px;  /* 6rem */
  --space-32: 128px; /* 8rem */
}
```

---

## Density Presets

### Compact Density
High information density, minimal padding. Good for dashboards, data-heavy UIs.

```css
:root[data-density="compact"] {
  /* Component spacing */
  --card-padding: var(--space-3);      /* 12px */
  --section-padding: var(--space-6);   /* 24px */
  --page-padding: var(--space-4);      /* 16px */

  /* Typography spacing */
  --heading-margin: var(--space-3);    /* 12px */
  --paragraph-margin: var(--space-2);  /* 8px */
  --list-gap: var(--space-1);          /* 4px */

  /* Interactive elements */
  --button-padding-x: var(--space-3);  /* 12px */
  --button-padding-y: var(--space-2);  /* 8px */
  --input-padding: var(--space-2);     /* 8px */

  /* Grid/Flex gaps */
  --grid-gap: var(--space-3);          /* 12px */
  --stack-gap: var(--space-2);         /* 8px */
}
```

**Tailwind Classes:**
```html
<div class="p-3 space-y-2">
  <h2 class="mb-3">Title</h2>
  <p class="mb-2">Content</p>
</div>
```

### Balanced Density (Default)
Standard spacing for most applications.

```css
:root[data-density="balanced"], :root {
  /* Component spacing */
  --card-padding: var(--space-6);      /* 24px */
  --section-padding: var(--space-12);  /* 48px */
  --page-padding: var(--space-6);      /* 24px */

  /* Typography spacing */
  --heading-margin: var(--space-6);    /* 24px */
  --paragraph-margin: var(--space-4);  /* 16px */
  --list-gap: var(--space-2);          /* 8px */

  /* Interactive elements */
  --button-padding-x: var(--space-4);  /* 16px */
  --button-padding-y: var(--space-3);  /* 12px */
  --input-padding: var(--space-3);     /* 12px */

  /* Grid/Flex gaps */
  --grid-gap: var(--space-6);          /* 24px */
  --stack-gap: var(--space-4);         /* 16px */
}
```

**Tailwind Classes:**
```html
<div class="p-6 space-y-4">
  <h2 class="mb-6">Title</h2>
  <p class="mb-4">Content</p>
</div>
```

### Spacious Density
Generous whitespace, breathing room. Good for editorial, luxury, marketing sites.

```css
:root[data-density="spacious"] {
  /* Component spacing */
  --card-padding: var(--space-8);      /* 32px */
  --section-padding: var(--space-24);  /* 96px */
  --page-padding: var(--space-8);      /* 32px */

  /* Typography spacing */
  --heading-margin: var(--space-10);   /* 40px */
  --paragraph-margin: var(--space-6);  /* 24px */
  --list-gap: var(--space-4);          /* 16px */

  /* Interactive elements */
  --button-padding-x: var(--space-8);  /* 32px */
  --button-padding-y: var(--space-4);  /* 16px */
  --input-padding: var(--space-4);     /* 16px */

  /* Grid/Flex gaps */
  --grid-gap: var(--space-10);         /* 40px */
  --stack-gap: var(--space-8);         /* 32px */
}
```

**Tailwind Classes:**
```html
<div class="p-8 space-y-8">
  <h2 class="mb-10">Title</h2>
  <p class="mb-6">Content</p>
</div>
```

---

## Component Spacing Patterns

### Cards
```css
/* Compact */
.card-compact {
  padding: 12px;
  gap: 8px;
}

/* Balanced */
.card-balanced {
  padding: 24px;
  gap: 16px;
}

/* Spacious */
.card-spacious {
  padding: 32px;
  gap: 24px;
}
```

### Sections
```css
/* Compact - Data dashboards */
.section-compact {
  padding-top: 24px;
  padding-bottom: 24px;
}

/* Balanced - Standard pages */
.section-balanced {
  padding-top: 48px;
  padding-bottom: 48px;
}

/* Spacious - Landing pages */
.section-spacious {
  padding-top: 96px;
  padding-bottom: 96px;
}
```

### Navigation
```css
/* Compact nav */
.nav-compact {
  height: 48px;
  padding: 0 16px;
}
.nav-compact .nav-link {
  padding: 8px 12px;
}

/* Balanced nav */
.nav-balanced {
  height: 64px;
  padding: 0 24px;
}
.nav-balanced .nav-link {
  padding: 12px 16px;
}

/* Spacious nav */
.nav-spacious {
  height: 80px;
  padding: 0 32px;
}
.nav-spacious .nav-link {
  padding: 16px 24px;
}
```

---

## Responsive Spacing

Adjust spacing based on viewport:

```css
/* Mobile-first approach */
.section {
  padding: var(--space-6) var(--space-4);
}

@media (min-width: 768px) {
  .section {
    padding: var(--space-12) var(--space-8);
  }
}

@media (min-width: 1024px) {
  .section {
    padding: var(--space-16) var(--space-12);
  }
}
```

### Tailwind Responsive Spacing
```html
<section class="py-6 px-4 md:py-12 md:px-8 lg:py-16 lg:px-12">
  <div class="space-y-4 md:space-y-6 lg:space-y-8">
    <!-- Content -->
  </div>
</section>
```

---

## Grid Systems

### 12-Column Grid
```css
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--grid-gap);
}

/* Responsive */
@media (max-width: 768px) {
  .grid-12 {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### Auto-fit Grid
```css
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--grid-gap);
}
```

### Asymmetric Grid (Editorial)
```css
.grid-editorial {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-12);
}

@media (max-width: 768px) {
  .grid-editorial {
    grid-template-columns: 1fr;
  }
}
```

---

## Container Widths

```css
:root {
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1536px;
}

.container {
  width: 100%;
  max-width: var(--container-xl);
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--page-padding);
  padding-right: var(--page-padding);
}

/* Narrow container for reading */
.container-prose {
  max-width: 65ch;
}

/* Wide container for full-bleed sections */
.container-wide {
  max-width: 100%;
  padding-left: var(--space-8);
  padding-right: var(--space-8);
}
```

---

## Typography Vertical Rhythm

Maintain consistent vertical rhythm with line-height multiples:

```css
:root {
  --line-height-base: 1.5;
  --rhythm-unit: calc(1rem * var(--line-height-base)); /* 24px */
}

h1 {
  font-size: 3rem;
  line-height: 1.1;
  margin-bottom: calc(var(--rhythm-unit) * 1.5);
}

h2 {
  font-size: 2rem;
  line-height: 1.2;
  margin-bottom: var(--rhythm-unit);
}

p {
  font-size: 1rem;
  line-height: var(--line-height-base);
  margin-bottom: var(--rhythm-unit);
}
```

---

## Quick Reference

| Density | Card Padding | Section Padding | Button Padding | Grid Gap |
|---------|--------------|-----------------|----------------|----------|
| Compact | 12px | 24px | 8px 12px | 12px |
| Balanced | 24px | 48px | 12px 16px | 24px |
| Spacious | 32px | 96px | 16px 32px | 40px |

| Use Case | Recommended Density |
|----------|---------------------|
| Dashboard/Admin | Compact |
| SaaS Product | Balanced |
| Marketing/Landing | Spacious |
| Editorial/Blog | Spacious |
| E-commerce | Balanced |
| Mobile App | Compact/Balanced |
