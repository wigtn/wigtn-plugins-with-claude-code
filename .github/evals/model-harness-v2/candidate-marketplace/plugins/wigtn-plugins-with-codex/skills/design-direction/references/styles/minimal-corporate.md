# Minimal Corporate Style Guide

## Overview
Minimal Corporate design is clean, professional, and trustworthy. It prioritizes clarity and function over decoration. Common in B2B SaaS, fintech, enterprise software, and professional services.

---

## Core Characteristics

| Aspect | Description |
|--------|-------------|
| Feel | Professional, trustworthy, efficient |
| Colors | Neutral palette with blue accents |
| Typography | Clean sans-serif, clear hierarchy |
| Spacing | Balanced, comfortable reading |
| UI | Functional, accessible, no decoration |

---

## Color Palette

### Light Mode
```css
:root {
  /* Base */
  --background: #ffffff;
  --foreground: #111827;

  /* Surface levels */
  --surface-1: #f9fafb;
  --surface-2: #f3f4f6;

  /* Primary (trustworthy blue) */
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-light: #eff6ff;

  /* Text */
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-tertiary: #9ca3af;

  /* Borders */
  --border: #e5e7eb;
  --border-hover: #d1d5db;

  /* Status */
  --success: #059669;
  --success-light: #d1fae5;
  --warning: #d97706;
  --warning-light: #fef3c7;
  --error: #dc2626;
  --error-light: #fee2e2;
  --info: #2563eb;
  --info-light: #dbeafe;
}
```

### Dark Mode
```css
.dark {
  --background: #111827;
  --foreground: #f9fafb;
  --surface-1: #1f2937;
  --surface-2: #374151;
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --primary-light: #1e3a5f;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-tertiary: #9ca3af;
  --border: #374151;
  --border-hover: #4b5563;
}
```

---

## Typography

### Recommended Fonts
- **Primary**: DM Sans, Satoshi, Inter, Plus Jakarta Sans
- **Monospace**: SF Mono, JetBrains Mono (for code/data)

### Hierarchy
```css
/* Page title */
h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

/* Section title */
h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

/* Card title */
h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* Body */
p {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* Small/Helper text */
.text-small {
  font-size: 0.875rem;
  color: var(--text-tertiary);
}

/* Label */
.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}
```

---

## Components

### Button
```css
/* Primary button */
.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 150ms ease;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-primary:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Secondary button */
.btn-secondary {
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-secondary:hover {
  background: var(--surface-1);
  border-color: var(--border-hover);
}

/* Ghost button */
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: none;
  padding: 10px 16px;
  font-size: 0.875rem;
}

.btn-ghost:hover {
  background: var(--surface-1);
  color: var(--text-primary);
}

/* Destructive */
.btn-destructive {
  background: var(--error);
  color: white;
}

.btn-destructive:hover {
  background: #b91c1c;
}
```

### Card
```css
.card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
}

.card-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.card-description {
  font-size: 0.875rem;
  color: var(--text-tertiary);
}

/* Elevated card (for important content) */
.card-elevated {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
}
```

### Input
```css
.input {
  width: 100%;
  background: white;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 0.875rem;
  color: var(--text-primary);
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.input:hover {
  border-color: var(--border-hover);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.input::placeholder {
  color: var(--text-tertiary);
}

/* Input with label */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

.input-hint {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

/* Error state */
.input-error {
  border-color: var(--error);
}

.input-error:focus {
  box-shadow: 0 0 0 3px var(--error-light);
}

.input-error-message {
  font-size: 0.75rem;
  color: var(--error);
}
```

### Table
```css
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-tertiary);
  background: var(--surface-1);
  border-bottom: 1px solid var(--border);
}

.table td {
  padding: 12px 16px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}

.table tr:hover td {
  background: var(--surface-1);
}
```

### Badge/Tag
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.badge-default {
  background: var(--surface-2);
  color: var(--text-secondary);
}

.badge-primary {
  background: var(--primary-light);
  color: var(--primary);
}

.badge-success {
  background: var(--success-light);
  color: var(--success);
}

.badge-warning {
  background: var(--warning-light);
  color: var(--warning);
}

.badge-error {
  background: var(--error-light);
  color: var(--error);
}
```

### Alert
```css
.alert {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 6px;
  font-size: 0.875rem;
}

.alert-info {
  background: var(--info-light);
  color: var(--info);
}

.alert-success {
  background: var(--success-light);
  color: var(--success);
}

.alert-warning {
  background: var(--warning-light);
  color: var(--warning);
}

.alert-error {
  background: var(--error-light);
  color: var(--error);
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}
```

---

## Layout Patterns

### Page Layout
```css
.page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-description {
  color: var(--text-secondary);
}
```

### Dashboard Grid
```css
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

/* Stats row */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
```

### Sidebar Layout
```css
.layout-sidebar {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--surface-1);
  border-right: 1px solid var(--border);
  padding: 24px 16px;
}

.main {
  padding: 24px;
}

@media (max-width: 768px) {
  .layout-sidebar {
    grid-template-columns: 1fr;
  }
}
```

---

## Navigation

### Top Navigation
```css
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  border-bottom: 1px solid var(--border);
  background: white;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 8px 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: 6px;
  transition: all 150ms ease;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--surface-1);
}

.nav-link.active {
  color: var(--primary);
  background: var(--primary-light);
}
```

### Sidebar Navigation
```css
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  border-radius: 6px;
}

.sidebar-link:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.sidebar-link.active {
  background: var(--primary-light);
  color: var(--primary);
}

.sidebar-link-icon {
  width: 20px;
  height: 20px;
}
```

---

## Forms

### Form Layout
```css
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 480px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
```

---

## Do's and Don'ts

### ✅ Do
- Use consistent spacing (8px base grid)
- Maintain clear visual hierarchy
- Use color sparingly (blue for actions, status colors for feedback)
- Provide clear focus states
- Keep layouts clean and organized
- Use icons to support (not replace) text labels

### ❌ Don't
- Add decorative elements
- Use more than 2-3 colors
- Use dark shadows or heavy borders
- Skip form validation feedback
- Overcrowd interfaces
- Use trendy effects (gradients, glows, etc.)
