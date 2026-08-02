# Dark Mode First Style Guide

## Overview
Dark Mode First design prioritizes dark backgrounds with high-contrast text and neon/vibrant accents. Popular for developer tools, gaming, music apps, and modern tech products. Creates a sleek, premium, futuristic feel.

---

## Core Characteristics

| Aspect | Description |
|--------|-------------|
| Feel | Technical, modern, premium, focused |
| Backgrounds | Deep blacks, dark grays |
| Accents | Neon colors with glow effects |
| Typography | Clean sans-serif or monospace |
| Borders | Subtle or glowing |

---

## Color Palette

### Primary Dark Theme
```css
:root {
  /* Backgrounds */
  --background: #09090b;          /* Near black */
  --background-elevated: #18181b;  /* Cards, modals */
  --background-hover: #27272a;     /* Hover states */

  /* Foreground */
  --foreground: #fafafa;
  --foreground-muted: #a1a1aa;
  --foreground-subtle: #71717a;

  /* Borders */
  --border: #27272a;
  --border-hover: #3f3f46;

  /* Neon Accents */
  --neon-purple: #a855f7;
  --neon-cyan: #22d3ee;
  --neon-pink: #ec4899;
  --neon-green: #22c55e;
  --neon-orange: #f97316;
  --neon-blue: #3b82f6;

  /* Primary accent (choose one) */
  --accent: var(--neon-purple);
  --accent-glow: rgba(168, 85, 247, 0.5);

  /* Status */
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
}
```

### Alternative: Deep Blue
```css
:root {
  --background: #0a0a1a;
  --background-elevated: #12122a;
  --accent: var(--neon-cyan);
  --accent-glow: rgba(34, 211, 238, 0.5);
}
```

---

## Typography

### Recommended Fonts
- **UI Text**: Inter, Geist, DM Sans
- **Code/Technical**: JetBrains Mono, Fira Code, SF Mono
- **Headlines**: Space Grotesk, Outfit

### Hierarchy
```css
h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--foreground);
}

h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--foreground);
}

p {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--foreground-muted);
}

code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  background: var(--background-elevated);
  padding: 2px 6px;
  border-radius: 4px;
}
```

---

## Glow Effects

### Text Glow
```css
.text-glow {
  color: var(--accent);
  text-shadow: 0 0 20px var(--accent-glow);
}

.text-glow-strong {
  text-shadow:
    0 0 10px var(--accent-glow),
    0 0 20px var(--accent-glow),
    0 0 40px var(--accent-glow);
}
```

### Box Glow
```css
.box-glow {
  box-shadow:
    0 0 20px var(--accent-glow),
    0 0 40px rgba(168, 85, 247, 0.2);
}

.box-glow-subtle {
  box-shadow: 0 0 15px var(--accent-glow);
}
```

### Border Glow
```css
.border-glow {
  border: 1px solid var(--accent);
  box-shadow:
    0 0 10px var(--accent-glow),
    inset 0 0 10px rgba(168, 85, 247, 0.1);
}
```

---

## Components

### Button
```css
/* Primary button with glow */
.btn-primary {
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms ease;
  box-shadow: 0 0 20px var(--accent-glow);
}

.btn-primary:hover {
  box-shadow:
    0 0 30px var(--accent-glow),
    0 0 60px rgba(168, 85, 247, 0.3);
  transform: translateY(-2px);
}

/* Ghost button */
.btn-ghost {
  background: transparent;
  color: var(--foreground);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 24px;
  transition: all 200ms ease;
}

.btn-ghost:hover {
  border-color: var(--accent);
  color: var(--accent);
  box-shadow: 0 0 15px var(--accent-glow);
}

/* Outline button */
.btn-outline {
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 12px 24px;
}

.btn-outline:hover {
  background: var(--accent);
  color: white;
  box-shadow: 0 0 20px var(--accent-glow);
}
```

### Card
```css
.card {
  background: var(--background-elevated);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  transition: all 200ms ease;
}

.card:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}

/* Feature card with glow */
.card-featured {
  background: var(--background-elevated);
  border: 1px solid var(--accent);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 0 30px var(--accent-glow);
}
```

### Input
```css
.input {
  background: var(--background-elevated);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  color: var(--foreground);
  font-size: 1rem;
  transition: all 200ms ease;
}

.input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 15px var(--accent-glow);
}

.input::placeholder {
  color: var(--foreground-subtle);
}
```

### Code Block
```css
.code-block {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.7;
  overflow-x: auto;
}

/* Syntax highlighting colors */
.token-keyword { color: var(--neon-purple); }
.token-string { color: var(--neon-green); }
.token-number { color: var(--neon-orange); }
.token-function { color: var(--neon-cyan); }
.token-comment { color: var(--foreground-subtle); }
```

### Badge
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-primary {
  background: rgba(168, 85, 247, 0.2);
  color: var(--neon-purple);
  border: 1px solid var(--neon-purple);
}

.badge-success {
  background: rgba(34, 197, 94, 0.2);
  color: var(--neon-green);
}
```

---

## Gradient Patterns

### Mesh Gradient Background
```css
.gradient-mesh {
  background-color: var(--background);
  background-image:
    radial-gradient(at 0% 0%, rgba(168, 85, 247, 0.3) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(34, 211, 238, 0.2) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.2) 0px, transparent 50%);
}
```

### Gradient Border
```css
.gradient-border {
  position: relative;
  background: var(--background-elevated);
  border-radius: 12px;
}

.gradient-border::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 1px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan));
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask-composite: exclude;
}
```

### Accent Gradient
```css
.gradient-accent {
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-pink));
}
```

---

## Layout Patterns

### Sidebar Layout (IDE-style)
```css
.layout-ide {
  display: grid;
  grid-template-columns: 60px 240px 1fr;
  min-height: 100vh;
}

.sidebar-icons {
  background: var(--background);
  border-right: 1px solid var(--border);
  padding: 16px 0;
}

.sidebar-nav {
  background: var(--background-elevated);
  border-right: 1px solid var(--border);
  padding: 16px;
}

.main-content {
  background: var(--background);
  padding: 24px;
}
```

### Terminal Style
```css
.terminal {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  overflow: hidden;
}

.terminal-header {
  background: var(--background-elevated);
  padding: 8px 12px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--border);
}

.terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.terminal-dot.red { background: #ef4444; }
.terminal-dot.yellow { background: #f59e0b; }
.terminal-dot.green { background: #22c55e; }

.terminal-body {
  padding: 16px;
  line-height: 1.7;
}

.terminal-prompt {
  color: var(--neon-green);
}
```

---

## Animations

### Glow Pulse
```css
@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 20px var(--accent-glow);
  }
  50% {
    box-shadow: 0 0 40px var(--accent-glow), 0 0 60px rgba(168, 85, 247, 0.3);
  }
}

.animate-glow {
  animation: glow-pulse 2s ease-in-out infinite;
}
```

### Subtle Float
```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
```

---

## Do's and Don'ts

### ✅ Do
- Use true blacks (#09090b, #000) for deep contrast
- Apply glow effects sparingly on key elements
- Use monospace fonts for technical content
- Ensure sufficient contrast (WCAG AA)
- Add subtle gradients for depth

### ❌ Don't
- Make everything glow (it loses impact)
- Use pure white text (too harsh, use #fafafa)
- Forget focus states (essential for accessibility)
- Overuse neon colors (pick 1-2 accents)
- Skip light mode entirely (offer as option)
