# Animation Systems

## Overview
This module provides animation patterns for different levels of motion design, from minimal to rich.

---

## Animation Levels

### Level 0: None
No animations. Use for:
- Users with `prefers-reduced-motion`
- Performance-critical applications
- Accessibility-first designs

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Level 1: Minimal
Hover states and focus indicators only.

```css
/* Hover opacity */
.hover-fade {
  transition: opacity 150ms ease;
}
.hover-fade:hover {
  opacity: 0.8;
}

/* Focus ring */
.focus-ring:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Button press */
.button-press {
  transition: transform 100ms ease;
}
.button-press:active {
  transform: scale(0.98);
}
```

### Level 2: Moderate
Page transitions, scroll reveals, micro-interactions.

```css
/* Fade in on scroll */
.fade-in-up {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 500ms ease, transform 500ms ease;
}
.fade-in-up.visible {
  opacity: 1;
  transform: translateY(0);
}

/* Card hover lift */
.card-lift {
  transition: transform 200ms ease, box-shadow 200ms ease;
}
.card-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Smooth page transitions */
.page-enter {
  opacity: 0;
  transform: translateX(20px);
}
.page-enter-active {
  opacity: 1;
  transform: translateX(0);
  transition: opacity 300ms ease, transform 300ms ease;
}
```

### Level 3: Rich
Complex animations, parallax, gesture-based interactions.

```css
/* Parallax scroll */
.parallax {
  transform: translateY(calc(var(--scroll-y) * 0.5));
}

/* Stagger animation */
.stagger-item {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeInUp 600ms ease forwards;
}
.stagger-item:nth-child(1) { animation-delay: 0ms; }
.stagger-item:nth-child(2) { animation-delay: 100ms; }
.stagger-item:nth-child(3) { animation-delay: 200ms; }
.stagger-item:nth-child(4) { animation-delay: 300ms; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Magnetic button effect */
.magnetic {
  transition: transform 300ms cubic-bezier(0.33, 1, 0.68, 1);
}

/* Morphing shapes */
.morph {
  animation: morph 8s ease-in-out infinite;
}
@keyframes morph {
  0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
  50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}
```

---

## Tailwind Animation Classes

Add to your CSS or Tailwind config:

```css
/* Base transitions */
.transition-fast { transition-duration: 150ms; }
.transition-normal { transition-duration: 300ms; }
.transition-slow { transition-duration: 500ms; }

/* Custom easing */
.ease-out-expo { transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1); }
.ease-in-out-expo { transition-timing-function: cubic-bezier(0.87, 0, 0.13, 1); }
.ease-spring { transition-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1); }

/* Hover animations */
.hover-scale:hover { transform: scale(1.02); }
.hover-lift:hover { transform: translateY(-2px); }
.hover-glow:hover { box-shadow: 0 0 20px var(--color-accent); }

/* Loading states */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-bounce {
  animation: bounce 1s infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(-5%); }
  50% { transform: translateY(0); }
}
```

---

## Intersection Observer (Scroll Animations)

```typescript
// React hook for scroll animations
function useScrollAnimation() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('.animate-on-scroll').forEach((el) => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);
}

// Usage
<div className="animate-on-scroll fade-in-up">Content</div>
```

---

## Page Transition Patterns

### Fade Transition
```tsx
// With Next.js App Router
'use client';
import { motion, AnimatePresence } from 'framer-motion';

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

### Slide Transition
```tsx
<motion.div
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -20 }}
  transition={{ duration: 0.3, ease: 'easeInOut' }}
>
  {children}
</motion.div>
```

---

## Micro-interactions

### Button States
```css
.btn {
  position: relative;
  overflow: hidden;
  transition: all 200ms ease;
}

/* Ripple effect */
.btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: currentColor;
  opacity: 0;
  transform: scale(0);
  border-radius: 50%;
  transition: transform 400ms ease, opacity 400ms ease;
}

.btn:active::after {
  transform: scale(2);
  opacity: 0.1;
  transition: transform 0ms, opacity 0ms;
}
```

### Input Focus
```css
.input {
  border: 1px solid var(--color-border);
  transition: border-color 200ms ease, box-shadow 200ms ease;
}

.input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(var(--color-accent-rgb), 0.1);
}
```

### Toggle Switch
```css
.toggle {
  position: relative;
  width: 48px;
  height: 24px;
  background: var(--color-muted);
  border-radius: 9999px;
  transition: background 200ms ease;
}

.toggle::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toggle.active {
  background: var(--color-accent);
}

.toggle.active::after {
  transform: translateX(24px);
}
```

---

## Performance Tips

### Use `transform` and `opacity`
These properties are GPU-accelerated and don't trigger layout:

```css
/* ✅ Good - GPU accelerated */
.good {
  transform: translateX(100px);
  opacity: 0.5;
}

/* ❌ Avoid - triggers layout */
.bad {
  left: 100px;
  width: 200px;
}
```

### Use `will-change` Sparingly
```css
/* Only on elements that will animate */
.will-animate {
  will-change: transform, opacity;
}
```

### Reduce Motion for Accessibility
```css
@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}
```

---

## Animation Timing Reference

| Duration | Use Case |
|----------|----------|
| 100ms | Button press, toggle |
| 150ms | Hover states, focus |
| 200ms | Small UI changes |
| 300ms | Page transitions, modals |
| 500ms | Scroll reveals |
| 600ms+ | Hero animations, complex sequences |

| Easing | Use Case |
|--------|----------|
| `ease` | General purpose |
| `ease-out` | Entrances |
| `ease-in` | Exits |
| `ease-in-out` | State changes |
| `cubic-bezier(0.34, 1.56, 0.64, 1)` | Bouncy/playful |
| `cubic-bezier(0.16, 1, 0.3, 1)` | Smooth deceleration |
