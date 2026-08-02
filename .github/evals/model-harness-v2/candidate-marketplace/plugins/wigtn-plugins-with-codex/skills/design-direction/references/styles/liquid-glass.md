# Liquid Glass Style Guide

## Core Philosophy
- Glass is alive — it refracts, distorts, and responds to its environment
- Depth through optical physics, not flat transparency
- Dynamic materials that shift with context
- Precision elegance: Apple-level craft in every surface
- The interface is a lens, not a wall

---

## Core Characteristics

| Aspect | Description |
|--------|-------------|
| Feel | Premium, fluid, alive, futuristic-yet-natural |
| Glass | Dynamic refraction, variable blur, light-responsive |
| Shadows | Soft, multi-layered, light source aware |
| Borders | Specular highlight edges (light reflection) |
| Color | Environment-adaptive, translucent tinting |
| Motion | Fluid, physics-based, responds to interaction |

---

## Liquid Glass vs Glassmorphism

| | Liquid Glass | Glassmorphism |
|--|-------------|---------------|
| Blur | Dynamic, variable per element | Static backdrop-filter |
| Refraction | Real distortion of background content | Simple transparency |
| Light | Specular highlights that shift | Fixed border highlight |
| Thickness | Variable — thin panes to thick lenses | Uniform |
| Color | Environment-derived tinting | Preset color overlays |
| Motion | Glass responds to scroll/hover | Static surfaces |
| Reference | Apple iOS 26 / macOS 26 | Windows Acrylic, early iOS |

---

## AI Slop Prevention Warning

Liquid Glass is the most technically demanding style.
**Absolutely avoid**:

- Slapping `backdrop-filter: blur()` everywhere and calling it liquid glass
- Static glass surfaces with no environmental response
- Purple/blue gradient backgrounds with white cards (that's generic glassmorphism)
- Uniform opacity across all glass elements
- Ignoring performance — blur is GPU-expensive

**Liquid Glass elements must feel like real optical materials.**

---

## Color Palette

### Environment-Adaptive System
```css
:root {
  /* Glass is tinted by its environment — these are base tints */
  --glass-tint-neutral: rgba(255, 255, 255, 0.12);
  --glass-tint-warm: rgba(255, 235, 210, 0.1);
  --glass-tint-cool: rgba(210, 230, 255, 0.1);

  /* Specular highlights (light reflections on glass edge) */
  --glass-specular: rgba(255, 255, 255, 0.5);
  --glass-specular-soft: rgba(255, 255, 255, 0.25);
  --glass-specular-subtle: rgba(255, 255, 255, 0.12);

  /* Shadow (glass casts soft, tinted shadows) */
  --glass-shadow: rgba(0, 0, 0, 0.08);
  --glass-shadow-deep: rgba(0, 0, 0, 0.16);
  --glass-shadow-tinted: rgba(100, 120, 160, 0.12);

  /* Text on glass */
  --glass-text-primary: rgba(0, 0, 0, 0.85);
  --glass-text-secondary: rgba(0, 0, 0, 0.55);
  --glass-text-tertiary: rgba(0, 0, 0, 0.35);

  /* Semantic accent */
  --glass-accent: #007AFF;
  --glass-accent-tint: rgba(0, 122, 255, 0.12);

  /* Background (must be rich for glass to work) */
  --glass-bg-light: #F2F2F7;
  --glass-bg-vibrant: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

/* Dark mode */
.dark {
  --glass-tint-neutral: rgba(255, 255, 255, 0.06);
  --glass-tint-warm: rgba(255, 200, 150, 0.05);
  --glass-tint-cool: rgba(150, 200, 255, 0.05);

  --glass-specular: rgba(255, 255, 255, 0.2);
  --glass-specular-soft: rgba(255, 255, 255, 0.1);
  --glass-specular-subtle: rgba(255, 255, 255, 0.05);

  --glass-shadow: rgba(0, 0, 0, 0.3);
  --glass-shadow-deep: rgba(0, 0, 0, 0.5);

  --glass-text-primary: rgba(255, 255, 255, 0.9);
  --glass-text-secondary: rgba(255, 255, 255, 0.6);
  --glass-text-tertiary: rgba(255, 255, 255, 0.35);

  --glass-bg-light: #000000;
}
```

---

## Typography

### Principles
- System fonts preferred (SF Pro for Apple feel, system-ui for cross-platform)
- Text must remain crisp on translucent surfaces
- Use text-shadow sparingly for legibility on variable backgrounds
- Weight: medium for labels, regular for body, semibold for headings

### Recommended Fonts
```css
/* System-native (recommended) */
--font-primary: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
--font-rounded: 'SF Pro Rounded', -apple-system, system-ui, sans-serif;

/* Web alternatives */
--font-primary: 'Inter', sans-serif;
--font-primary: 'Geist', sans-serif;

/* Monospace (for labels, data) */
--font-mono: 'SF Mono', 'Geist Mono', monospace;
```

### Type Scale
```css
--text-title-1: 1.75rem;  /* 28px */
--text-title-2: 1.375rem; /* 22px */
--text-title-3: 1.125rem; /* 18px */
--text-body: 1rem;         /* 16px */
--text-callout: 0.9375rem; /* 15px */
--text-footnote: 0.8125rem; /* 13px */
--text-caption: 0.75rem;   /* 12px */
```

### Text on Glass
```css
.lg-text-on-glass {
  color: var(--glass-text-primary);
  /* Subtle shadow for readability on variable backgrounds */
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
}

.dark .lg-text-on-glass {
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
}

.lg-label {
  font-size: var(--text-footnote);
  font-weight: 500;
  color: var(--glass-text-secondary);
  letter-spacing: 0.02em;
}
```

---

## The Liquid Glass Effect (Core Identity)

### Thin Glass (Navigation bars, tab bars)
```css
.lg-thin {
  background: var(--glass-tint-neutral);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 0.5px solid var(--glass-specular-subtle);
  /* Top specular highlight */
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular-soft),
    0 2px 8px var(--glass-shadow);
}
```

### Standard Glass (Cards, panels, modals)
```css
.lg-standard {
  background: var(--glass-tint-neutral);
  backdrop-filter: blur(40px) saturate(200%) brightness(1.05);
  -webkit-backdrop-filter: blur(40px) saturate(200%) brightness(1.05);
  border-radius: 20px;
  border: 0.5px solid var(--glass-specular-subtle);
  box-shadow:
    /* Specular edge highlight (top + left) */
    inset 0 0.5px 0 var(--glass-specular),
    inset 0.5px 0 0 var(--glass-specular-soft),
    /* Ambient shadow */
    0 4px 16px var(--glass-shadow),
    0 8px 32px var(--glass-shadow-tinted);
}
```

### Thick Glass (Hero elements, floating panels)
```css
.lg-thick {
  background:
    linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.15) 0%,
      rgba(255, 255, 255, 0.05) 50%,
      rgba(255, 255, 255, 0.1) 100%
    );
  backdrop-filter: blur(60px) saturate(220%) brightness(1.1);
  -webkit-backdrop-filter: blur(60px) saturate(220%) brightness(1.1);
  border-radius: 24px;
  border: 0.5px solid var(--glass-specular-soft);
  box-shadow:
    /* Strong specular highlights */
    inset 0 1px 0 var(--glass-specular),
    inset 1px 0 0 var(--glass-specular-soft),
    inset 0 -0.5px 0 rgba(255, 255, 255, 0.05),
    /* Deep shadow */
    0 8px 32px var(--glass-shadow-deep),
    0 16px 48px var(--glass-shadow-tinted);
}
```

### Frosted Glass (Sidebars, overlays)
```css
.lg-frosted {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(80px) saturate(150%);
  -webkit-backdrop-filter: blur(80px) saturate(150%);
  border-radius: 16px;
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  box-shadow:
    inset 0 0.5px 0 rgba(255, 255, 255, 0.5),
    0 2px 12px var(--glass-shadow);
}

.dark .lg-frosted {
  background: rgba(30, 30, 30, 0.7);
  border-color: rgba(255, 255, 255, 0.08);
}
```

---

## Dynamic Refraction Effect

### CSS-Based Refraction (Distortion)
```css
/* Content behind glass appears distorted */
.lg-refract {
  position: relative;
  overflow: hidden;
}

.lg-refract::before {
  content: '';
  position: absolute;
  inset: 0;
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  /* Refraction gradient — simulates lens curvature */
  mask-image: radial-gradient(
    ellipse 80% 80% at 50% 50%,
    black 40%,
    transparent 100%
  );
  -webkit-mask-image: radial-gradient(
    ellipse 80% 80% at 50% 50%,
    black 40%,
    transparent 100%
  );
  z-index: 0;
}

.lg-refract > * {
  position: relative;
  z-index: 1;
}
```

### Light Response (Specular Shift on Hover/Scroll)
```css
/* Specular highlight shifts based on mouse position */
.lg-responsive {
  position: relative;
  overflow: hidden;
}

.lg-responsive::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle 200px at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(255, 255, 255, 0.15) 0%,
    transparent 80%
  );
  pointer-events: none;
  transition: opacity 0.3s ease;
  opacity: 0;
}

.lg-responsive:hover::after {
  opacity: 1;
}
```

### JavaScript: Mouse-Tracking Light
```javascript
// Apply to .lg-responsive elements
function initLiquidGlass(element) {
  element.addEventListener('mousemove', (e) => {
    const rect = element.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    element.style.setProperty('--mouse-x', `${x}%`);
    element.style.setProperty('--mouse-y', `${y}%`);
  });
}

document.querySelectorAll('.lg-responsive').forEach(initLiquidGlass);
```

---

## UI Components

### Button
```css
.lg-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: var(--text-callout);
  font-weight: 500;
  color: var(--glass-text-primary);
  background: var(--glass-tint-neutral);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 0.5px solid var(--glass-specular-subtle);
  border-radius: 12px;
  cursor: pointer;
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular-soft),
    0 2px 8px var(--glass-shadow);
  transition: all 0.2s ease;
}

.lg-button:hover {
  background: rgba(255, 255, 255, 0.2);
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular),
    0 4px 12px var(--glass-shadow);
  transform: translateY(-1px);
}

.lg-button:active {
  transform: translateY(0);
  background: rgba(255, 255, 255, 0.08);
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular-subtle),
    0 1px 4px var(--glass-shadow);
}

/* Accent button */
.lg-button-accent {
  background: var(--glass-accent);
  color: white;
  border-color: transparent;
  backdrop-filter: none;
  box-shadow:
    0 2px 8px rgba(0, 122, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.lg-button-accent:hover {
  box-shadow:
    0 4px 16px rgba(0, 122, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
}
```

### Card
```css
.lg-card {
  padding: 20px;
  border-radius: 20px;
  background: var(--glass-tint-neutral);
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  border: 0.5px solid var(--glass-specular-subtle);
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular),
    0 4px 16px var(--glass-shadow),
    0 8px 32px var(--glass-shadow-tinted);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.lg-card:hover {
  transform: translateY(-2px);
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular),
    0 8px 24px var(--glass-shadow),
    0 16px 48px var(--glass-shadow-tinted);
}
```

### Input
```css
.lg-input {
  width: 100%;
  padding: 10px 14px;
  font-size: var(--text-body);
  color: var(--glass-text-primary);
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 0.5px solid var(--glass-specular-subtle);
  border-radius: 10px;
  box-shadow: inset 0 0.5px 0 var(--glass-specular-subtle);
  transition: all 0.2s ease;
}

.lg-input:focus {
  outline: none;
  border-color: var(--glass-accent);
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular-subtle),
    0 0 0 3px var(--glass-accent-tint);
}

.lg-input::placeholder {
  color: var(--glass-text-tertiary);
}
```

### Navigation Bar
```css
.lg-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--glass-tint-neutral);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 0.5px solid var(--glass-specular-subtle);
  box-shadow:
    inset 0 -0.5px 0 rgba(0, 0, 0, 0.05),
    0 1px 4px var(--glass-shadow);
}
```

### Modal / Sheet
```css
.lg-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 200;
}

.lg-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 201;
  min-width: 400px;
  max-width: 90vw;
  padding: 28px;
  border-radius: 24px;
  background:
    linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.2) 0%,
      rgba(255, 255, 255, 0.08) 100%
    );
  backdrop-filter: blur(60px) saturate(200%) brightness(1.05);
  -webkit-backdrop-filter: blur(60px) saturate(200%) brightness(1.05);
  border: 0.5px solid var(--glass-specular-soft);
  box-shadow:
    inset 0 1px 0 var(--glass-specular),
    0 16px 48px var(--glass-shadow-deep),
    0 32px 80px rgba(0, 0, 0, 0.12);
}
```

### Tab Bar (iOS-style)
```css
.lg-tab-bar {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 14px;
  border: 0.5px solid var(--glass-specular-subtle);
}

.lg-tab {
  flex: 1;
  padding: 8px 16px;
  font-size: var(--text-footnote);
  font-weight: 500;
  color: var(--glass-text-secondary);
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.lg-tab.active {
  color: var(--glass-text-primary);
  background: var(--glass-tint-neutral);
  backdrop-filter: blur(20px);
  box-shadow:
    inset 0 0.5px 0 var(--glass-specular-soft),
    0 2px 8px var(--glass-shadow);
}
```

---

## Background Requirements

### Principles
- Liquid glass REQUIRES a rich, colorful background to work
- Mesh gradients, photography, or vibrant UI behind the glass
- Plain solid backgrounds make glass invisible

```css
/* Mesh gradient background */
.lg-bg-mesh {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(255, 119, 115, 0.2) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(78, 205, 196, 0.2) 0%, transparent 40%),
    var(--glass-bg-light);
  min-height: 100vh;
}

/* Animated gradient orbs */
.lg-bg-orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: lgOrbit 25s ease-in-out infinite;
}

.lg-bg-orb-1 {
  width: 40vw;
  height: 40vw;
  background: #7877C6;
  top: -10%;
  left: 10%;
}

.lg-bg-orb-2 {
  width: 35vw;
  height: 35vw;
  background: #FF7773;
  bottom: -10%;
  right: 10%;
  animation-delay: -8s;
}

.lg-bg-orb-3 {
  width: 30vw;
  height: 30vw;
  background: #4ECDC4;
  top: 50%;
  left: 50%;
  animation-delay: -16s;
}

@keyframes lgOrbit {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(5%, -8%) scale(1.05); }
  50% { transform: translate(-3%, 5%) scale(0.95); }
  75% { transform: translate(-5%, -3%) scale(1.02); }
}
```

---

## Layout

```css
/* Glass container */
.lg-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

/* Floating glass panel */
.lg-panel {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  min-height: 80vh;
}

/* Glass sidebar */
.lg-sidebar {
  padding: 20px;
  border-radius: 20px;
  height: fit-content;
  position: sticky;
  top: 100px;
}

/* Card grid */
.lg-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
```

---

## Interaction & Motion

### Principles
- Fluid, physics-based motion (spring curves)
- Glass surfaces respond to interaction (specular shift)
- Transitions feel like moving through liquid
- Subtle parallax between glass layers

```css
/* Fluid hover */
.lg-fluid {
  transition:
    transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    box-shadow 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Appear animation */
.lg-appear {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
  animation: lgAppear 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

@keyframes lgAppear {
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Modal enter */
.lg-modal-enter {
  animation: lgModalIn 0.4s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}

@keyframes lgModalIn {
  from {
    opacity: 0;
    transform: translate(-50%, -48%) scale(0.95);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
    filter: blur(0);
  }
}

/* Parallax between glass layers */
.lg-parallax-container {
  perspective: 1000px;
}

.lg-parallax-layer-1 {
  transform: translateZ(0px);
}

.lg-parallax-layer-2 {
  transform: translateZ(20px);
}

.lg-parallax-layer-3 {
  transform: translateZ(40px);
}

/* Stagger */
.lg-stagger > * {
  opacity: 0;
  animation: lgAppear 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

.lg-stagger > *:nth-child(1) { animation-delay: 0ms; }
.lg-stagger > *:nth-child(2) { animation-delay: 60ms; }
.lg-stagger > *:nth-child(3) { animation-delay: 120ms; }
.lg-stagger > *:nth-child(4) { animation-delay: 180ms; }
```

---

## Performance Considerations

```css
/* Opt-in GPU acceleration */
.lg-gpu {
  will-change: transform;
  transform: translateZ(0);
}

/* Reduce blur on low-power devices */
@media (prefers-reduced-motion: reduce) {
  .lg-standard,
  .lg-thick,
  .lg-thin {
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
  }

  .lg-appear,
  .lg-modal-enter {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

/* Fallback for browsers without backdrop-filter */
@supports not (backdrop-filter: blur(1px)) {
  .lg-standard,
  .lg-thick,
  .lg-thin,
  .lg-frosted {
    background: rgba(255, 255, 255, 0.85);
  }

  .dark .lg-standard,
  .dark .lg-thick,
  .dark .lg-thin,
  .dark .lg-frosted {
    background: rgba(30, 30, 30, 0.9);
  }
}
```

---

## Absolute Avoid List

- Static, uniform blur on all elements (use variable blur levels)
- Solid white/gray backgrounds (glass needs colorful content behind it)
- Heavy borders (0.5px max — glass edges are specular, not structural)
- Excessive backdrop-filter stacking (performance killer)
- Ignoring dark mode (glass looks fundamentally different)
- Using glassmorphism patterns unchanged (liquid glass is evolved, not the same)
- Rainbow or neon gradient backgrounds (keep it sophisticated)
- Forgetting `@supports` fallback for non-supporting browsers

---

## Inspiration Keywords

- Apple iOS 26 / macOS 26 design language
- Frosted glass architecture
- Camera lens optics
- Water droplet refraction
- Crystal prism light splitting
- Automotive HUD displays
- Museum glass display cases

---

## Final Check

> Every glass surface should feel like a real optical material — not a transparent div.
> The specular highlight (inset 0 0.5px 0) is what makes it liquid glass, not just glass.
> Background richness determines glass quality. Plain bg = invisible glass.
> Test on dark mode. Test the fallback. Test performance on mobile.
