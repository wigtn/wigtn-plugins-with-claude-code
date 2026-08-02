# Color Systems

## Overview
This module provides color palette systems and implementation patterns for all design styles.

---

## CSS Variable Structure

색은 일관성·테마 전환을 위해 CSS custom properties로 정의한다:

```css
:root {
  /* Base colors */
  --color-background: #ffffff;
  --color-foreground: #0a0a0a;

  /* Primary palette */
  --color-primary: #0066ff;
  --color-primary-foreground: #ffffff;

  /* Secondary palette */
  --color-secondary: #f4f4f5;
  --color-secondary-foreground: #18181b;

  /* Accent */
  --color-accent: #0066ff;
  --color-accent-foreground: #ffffff;

  /* Semantic colors */
  --color-muted: #f4f4f5;
  --color-muted-foreground: #71717a;
  --color-border: #e4e4e7;

  /* Status colors */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
}

.dark {
  --color-background: #0a0a0a;
  --color-foreground: #fafafa;
  --color-primary: #3b82f6;
  --color-secondary: #27272a;
  --color-secondary-foreground: #fafafa;
  --color-muted: #27272a;
  --color-muted-foreground: #a1a1aa;
  --color-border: #27272a;
}
```

---

## Color Palette Presets

### Monochrome
```css
:root {
  --color-background: #ffffff;
  --color-foreground: #0a0a0a;
  --color-accent: #0066ff; /* Single accent */
  --color-muted: #f5f5f5;
  --color-muted-foreground: #737373;
  --color-border: #e5e5e5;
}

.dark {
  --color-background: #0a0a0a;
  --color-foreground: #fafafa;
  --color-accent: #3b82f6;
  --color-muted: #262626;
  --color-muted-foreground: #a3a3a3;
  --color-border: #262626;
}
```

### Vibrant
```css
:root {
  --color-background: #ffffff;
  --color-foreground: #1a1a2e;
  --color-primary: #e94560;
  --color-secondary: #0f3460;
  --color-accent: #16213e;
  --color-success: #00d9a5;
  --color-warning: #ffc107;
}
```

### Earthy
```css
:root {
  --color-background: #faf8f5;
  --color-foreground: #2d2a26;
  --color-primary: #8b7355;
  --color-secondary: #c4b7a6;
  --color-accent: #6b8e23;
  --color-muted: #e8e4de;
  --color-border: #d4cfc6;
}

.dark {
  --color-background: #1a1815;
  --color-foreground: #e8e4de;
  --color-primary: #a89078;
  --color-muted: #2d2a26;
  --color-border: #3d3833;
}
```

### Cool (Blues & Teals)
```css
:root {
  --color-background: #f8fafc;
  --color-foreground: #0f172a;
  --color-primary: #0ea5e9;
  --color-secondary: #06b6d4;
  --color-accent: #6366f1;
  --color-muted: #f1f5f9;
  --color-border: #e2e8f0;
}

.dark {
  --color-background: #0f172a;
  --color-foreground: #f8fafc;
  --color-primary: #38bdf8;
  --color-muted: #1e293b;
  --color-border: #334155;
}
```

### Warm (Oranges & Reds)
```css
:root {
  --color-background: #fffbf5;
  --color-foreground: #1c1917;
  --color-primary: #ea580c;
  --color-secondary: #dc2626;
  --color-accent: #ca8a04;
  --color-muted: #fef3e2;
  --color-border: #fed7aa;
}

.dark {
  --color-background: #1c1917;
  --color-foreground: #fef3e2;
  --color-primary: #fb923c;
  --color-muted: #292524;
  --color-border: #44403c;
}
```

### Dark (For Dark Mode First)
```css
:root {
  --color-background: #09090b;
  --color-foreground: #fafafa;
  --color-primary: #a855f7;
  --color-secondary: #06b6d4;
  --color-accent: #22d3ee;
  --color-muted: #18181b;
  --color-muted-foreground: #a1a1aa;
  --color-border: #27272a;

  /* Neon accents for glow effects */
  --color-neon-purple: #a855f7;
  --color-neon-cyan: #22d3ee;
  --color-neon-pink: #ec4899;
  --color-neon-green: #22c55e;
}
```

---

## Gradient Presets

### Subtle Gradients
```css
.gradient-subtle-light {
  background: linear-gradient(180deg, #ffffff 0%, #f5f5f5 100%);
}

.gradient-subtle-blue {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.gradient-subtle-overlay {
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.02) 100%);
}
```

### Bold Gradients
```css
.gradient-bold-sunset {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-bold-ocean {
  background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
}

.gradient-bold-fire {
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
}

.gradient-bold-nature {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}
```

### Mesh Gradients
```css
.gradient-mesh {
  background-color: #ff99ee;
  background-image:
    radial-gradient(at 80% 0%, #ff99ee 0px, transparent 50%),
    radial-gradient(at 0% 50%, #99ccff 0px, transparent 50%),
    radial-gradient(at 80% 50%, #ffcc99 0px, transparent 50%),
    radial-gradient(at 0% 100%, #99ffcc 0px, transparent 50%);
}

.gradient-mesh-dark {
  background-color: #1a1a2e;
  background-image:
    radial-gradient(at 80% 0%, rgba(168, 85, 247, 0.4) 0px, transparent 50%),
    radial-gradient(at 0% 50%, rgba(34, 211, 238, 0.3) 0px, transparent 50%),
    radial-gradient(at 80% 50%, rgba(236, 72, 153, 0.3) 0px, transparent 50%);
}
```

---

## Tailwind CSS Integration

Add to `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        background: 'var(--color-background)',
        foreground: 'var(--color-foreground)',
        primary: {
          DEFAULT: 'var(--color-primary)',
          foreground: 'var(--color-primary-foreground)',
        },
        secondary: {
          DEFAULT: 'var(--color-secondary)',
          foreground: 'var(--color-secondary-foreground)',
        },
        accent: {
          DEFAULT: 'var(--color-accent)',
          foreground: 'var(--color-accent-foreground)',
        },
        muted: {
          DEFAULT: 'var(--color-muted)',
          foreground: 'var(--color-muted-foreground)',
        },
        border: 'var(--color-border)',
      },
    },
  },
}
```

---

## Dark Mode Implementation

### Method 1: CSS Class Toggle
```javascript
// Toggle dark mode
document.documentElement.classList.toggle('dark');

// Check system preference
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.classList.add('dark');
}
```

### Method 2: Data Attribute
```css
[data-theme="dark"] {
  --color-background: #0a0a0a;
  /* ... */
}
```

### React Theme Toggle Example
```tsx
function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDark(stored === 'dark' || (!stored && prefersDark));
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <button onClick={() => setIsDark(!isDark)}>
      {isDark ? '☀️' : '🌙'}
    </button>
  );
}
```

---

## Accessibility Guidelines

### Contrast Requirements
- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text (18px+)**: Minimum 3:1 contrast ratio
- **UI components**: Minimum 3:1 contrast ratio

### Testing Tools
- Chrome DevTools (Accessibility panel)
- WebAIM Contrast Checker
- Figma A11y plugins

### Common Issues to Avoid
```css
/* ❌ Poor contrast */
.bad {
  color: #999999;
  background: #ffffff; /* 2.85:1 ratio - FAIL */
}

/* ✅ Good contrast */
.good {
  color: #737373;
  background: #ffffff; /* 4.54:1 ratio - PASS */
}
```

---

## Color Usage Patterns

### Text Colors
```css
.text-primary { color: var(--color-foreground); }
.text-secondary { color: var(--color-muted-foreground); }
.text-accent { color: var(--color-accent); }
```

### Background Colors
```css
.bg-base { background: var(--color-background); }
.bg-elevated { background: var(--color-muted); }
.bg-accent { background: var(--color-accent); }
```

### Border Colors
```css
.border-default { border-color: var(--color-border); }
.border-accent { border-color: var(--color-accent); }
```
