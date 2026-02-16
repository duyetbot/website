# Modern CSS Modernization Plan

**Date:** 2026-02-16
**Sources:** [Modern CSS Code Snippets](https://modern-css.com/), [Oat UI Library](https://oat.ink/)

## Projects

| Project | Current Stack | Goal |
|---------|--------------|------|
| **~/projects/website** | Python SSG + Oat CSS | Enhance Oat with modern CSS |
| **~/projects/website/interactive** | Next.js + Tailwind | Add modern CSS utilities |
| **duet-company/apps/frontend** | Next.js skeleton | Build with modern CSS + Oat/Tailwind |

---

## Priority 1: Quick Wins (Apply Everywhere)

### 1.1 Color System Upgrade → OKLCH

**Old Way:**
```css
:root {
  --color-bg: #faf9f7;
  --color-accent: #6366f1;
}
```

**Modern Way:**
```css
:root {
  --color-bg: oklch(98% 0.005 85);   /* warm off-white */
  --color-accent: oklch(0.55 0.2 264); /* indigo */
  --color-accent-hover: oklch(from var(--color-accent) calc(l - 0.1) c h);
}
```

**Benefits:**
- Perceptually uniform colors
- Generate lighter/darker shades without hue shifts
- Better dark mode consistency

### 1.2 Spacing → `gap` instead of margin hacks

**Old Way:**
```css
.grid > * {
  margin-right: 1.5rem;
}
.grid > *:last-child {
  margin-right: 0;
}
```

**Modern Way:**
```css
.grid {
  display: flex;
  gap: 1.5rem;
}
```

### 1.3 Aspect Ratio

**Old Way:**
```css
.video-wrapper {
  padding-top: 56.25%; /* 16:9 aspect ratio */
  position: relative;
}
.video-wrapper .inner {
  position: absolute;
  inset: 0;
}
```

**Modern Way:**
```css
.video-wrapper {
  aspect-ratio: 16/9;
}
```

### 1.4 Position Shorthand

**Old Way:**
```css
.overlay {
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
```

**Modern Way:**
```css
.overlay {
  inset: 0;
}
```

### 1.5 Centering with Grid

**Old Way:**
```css
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}
```

**Modern Way:**
```css
.centered {
  display: grid;
  place-items: center;
}
```

---

## Priority 2: Dark Mode Improvements

### 2.1 Light-Dark Color Function

**Old Way:**
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f172a;
    --color-text: #f8fafc;
  }
}
```

**Modern Way:**
```css
:root {
  color-scheme: light dark;
  --color-bg: light-dark(#faf9f7, #0f172a);
  --color-text: light-dark(#1a1a1a, #f8fafc);
}
```

### 2.2 Mix Colors Without Preprocessor

**Old Way:**
```css
/* Requires Sass: */
.button {
  background: mix($brand, $bg, 80%);
}
```

**Modern Way:**
```css
.button {
  background: color-mix(in oklch, var(--color-accent), var(--color-bg) 80%);
}
```

---

## Priority 3: CSS Nesting

### 3.1 Native Nesting (No More SCSS)

**Old Way:**
```scss
.card {
  padding: 1.5rem;
  & h3 {
    font-size: 1rem;
  }
  &:hover {
    border-color: var(--color-accent);
  }
}
```

**Modern Way:**
```css
.card {
  padding: 1.5rem;

  h3 {
    font-size: 1rem;
  }

  &:hover {
    border-color: var(--color-accent);
  }
}
```

### 3.2 Reverse Context Selector

**Old Way:**
```scss
/* Can't do this in SCSS */
.featured .card { }
```

**Modern Way:**
```css
.card {
  .featured & {
    border-color: var(--color-accent);
  }
}
```

---

## Priority 4: New Selectors & Pseudo-classes

### 4.1 :has() - Parent Selector

**Use Case:** Style cards differently when they contain an image

**Modern Way:**
```css
.post-card:has(img) {
  grid-template-columns: auto 1fr;
}
```

### 4.2 :is() and :where()

**Old Way:**
```css
.card h1,
.card h2,
.card h3,
.card h4 {
  margin-bottom: 0.5rem;
}
```

**Modern Way:**
```css
.card :is(h1, h2, h3, h4) {
  margin-bottom: 0.5rem;
}
```

**For Reset Styles (zero specificity):**
```css
:where(ul, ol) {
  margin: 0;
  padding-inline-start: 1.5rem;
}
```

### 4.3 :user-invalid / :user-valid

**Old Way:**
```javascript
// JS needed
input.addEventListener('blur', () => input.classList.add('touched'));
```
```css
input.touched:invalid {
  border-color: red;
}
```

**Modern Way:**
```css
input:user-invalid {
  border-color: #ef4444;
}

input:user-valid {
  border-color: #22c55e;
}
```

### 4.4 text-box: trim - Optical Text Centering

**Old Way:**
```css
h1, button {
  /* Manual padding tweaks needed */
  padding-top: 8px;  /* hack to visually center */
}
```

**Modern Way:**
```css
h1, button {
  text-box: trim-both cap alphabetic;
}
```

---

## Priority 5: Container Queries

### 5.1 Responsive Components

**Old Way:**
```css
@media (max-width: 600px) {
  .card {
    flex-direction: column;
  }
}
```

**Modern Way:**
```css
@container (width < 400px) {
  .card {
    flex-direction: column;
  }
}
```

### 5.2 Container Style Queries

**Old Way:**
```scss
// Multiple media queries
@container style(--p: 50%) { }
@container style(--p: 51%) { }
@container style(--p: 52%) { }
```

**Modern Way:**
```css
@container style(--progress > 50%) {
  .progress-bar {
    background: var(--color-accent);
  }
}
```

---

## Priority 6: Modern Typography

### 6.1 Fluid Typography

**Old Way:**
```css
h1 {
  font-size: 1rem;
}
@media (min-width: 600px) {
  h1 {
    font-size: 1.5rem;
  }
}
@media (min-width: 900px) {
  h1 {
    font-size: 2rem;
  }
}
```

**Modern Way:**
```css
h1 {
  font-size: clamp(1rem, 2.5vw, 2rem);
}
```

### 6.2 Text Wrap Balance

**Old Way:**
```html
<!-- Manual line breaks -->
<h1>Building AI<br>Agents with<br>Rust</h1>
```

**Modern Way:**
```css
h1, h2 {
  text-wrap: balance;
}
```

### 6.3 Line Clamp

**Old Way:**
```css
.card-title {
  overflow: hidden;
  /* Multiple lines + JS needed */
}
```

**Modern Way:**
```css
.card-title {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

### 6.4 Drop Caps

**Old Way:**
```css
.drop-cap::first-letter {
  float: left;
  font-size: 3em;
  line-height: 1;
  margin-right: 0.1em;
}
```

**Modern Way:**
```css
.drop-cap::first-letter {
  initial-letter: 3;
}
```

---

## Priority 7: Animations & Transitions

### 7.1 Smooth Height Auto Animation

**Old Way:**
```javascript
// JS needed
el.style.height = el.scrollHeight + 'px';
el.addEventListener('transitionend', ...);
```

**Modern Way:**
```css
:root {
  interpolate-size: allow-keywords;
}

.accordion {
  height: 0;
  overflow: hidden;
  transition: height 0.3s ease;
}

.accordion.open {
  height: auto;
}
```

### 7.2 Entry Animations

**Old Way:**
```javascript
// rAF or setTimeout needed
requestAnimationFrame(() => {
  el.classList.add('visible');
});
```

**Modern Way:**
```css
.card {
  transition: opacity 0.3s, transform 0.3s;
}

@starting-style {
  .card {
    opacity: 0;
    transform: translateY(10px);
  }
}
```

### 7.3 Independent Transforms

**Old Way:**
```css
.icon {
  transform: translateX(10px) rotate(45deg) scale(1.2);
}
/* Change one = rewrite all */
```

**Modern Way:**
```css
.icon {
  translate: 10px 0;
  rotate: 45deg;
  scale: 1.2;
}
/* Animate any one without touching the rest */
```

### 7.4 Animation Display Without Workarounds

**Old Way:**
```javascript
// Need to wait for transitionend
el.addEventListener('transitionend', () => {
  el.style.display = 'none';
});
```

**Modern Way:**
```css
.panel {
  transition: opacity 0.2s, overlay 0.2s;
  transition-behavior: allow-discrete;
}

.panel.hidden {
  opacity: 0;
  display: none;
}
```

---

## Priority 8: Form Improvements

### 8.1 Auto-Growing Textarea

**Old Way:**
```javascript
el.addEventListener('input', () => {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
});
```

**Modern Way:**
```css
textarea {
  field-sizing: content;
  min-height: 3lh;
}
```

### 8.2 Native Dialog Backdrop

**Old Way:**
```javascript
// JS listener needed
dialog.addEventListener('click', (e) => {
  if (e.target === dialog) dialog.close();
});
```

**Modern Way:**
```html
<dialog>
  <form method="dialog">
    <button>CANCEL</button>
  </form>
</dialog>
```
```css
dialog::backdrop {
  background: rgb(0 0 0 / 0.5);
}
```

---

## Priority 9: Oat Integration Patterns

### 9.1 Semantic HTML + Modern CSS

Oat's philosophy: Style native elements without classes

**Old Way (Tailwind):**
```html
<div class="flex items-center justify-center p-4 bg-blue-500 text-white rounded-lg">
  <button class="px-4 py-2">Click me</button>
</div>
```

**Modern Way (Oat + Modern CSS):**
```html
<div class="card">
  <button>Action</button>
</div>
```
```css
.card {
  display: grid;
  place-items: center;
  padding: 1rem;
  background: var(--color-accent);
  color: white;
}

button {
  padding: 0.5rem 1rem;
}
```

### 9.2 Scoped Styles

**Modern CSS has native @scope:**
```css
@scope (.card) {
  .title {
    /* Only applies .title inside .card */
    font-size: 1.25rem;
  }
}
```

---

## Priority 10: Browser Support Strategy

### Check Support Before Using

```bash
# Can I Use checker
curl -s "https://caniuse.com/process/query.json?searches=oklch"
```

### Fallback Strategy

```css
/* Progressive enhancement */
.card {
  background: var(--color-bg); /* Fallback */
  background: oklch(98% 0.005 85); /* Modern */
}
```

### When to Skip Modern CSS

**Skip if:**
- Requires Safari < 16 and you have Safari users
- Feature is < 80% browser support
- You're building for legacy enterprise environments

**Use if:**
- Internal tools (controlled browser environment)
- Progressive web app (modern browsers only)
- Personal projects (your choice)

---

## Implementation Plan

### Phase 1: ~/projects/website (Oat-based)

**Tasks:**
1. ✅ Convert color system to OKLCH
2. ✅ Replace margin hacks with `gap`
3. ✅ Add `text-box: trim` for headings
4. ✅ Update dark mode to `color-scheme` + `light-dark()`
5. ✅ Add native CSS nesting
6. ✅ Use `:has()`, `:is()`, `:where()` selectors
7. ✅ Add `text-wrap: balance` for headings
8. ✅ Smooth animations with `@starting-style`

**Estimated:** 2-3 hours

### Phase 2: ~/projects/website/interactive (Tailwind-based)

**Tasks:**
1. Create modern CSS utility classes
2. Add custom Tailwind config for OKLCH colors
3. Create `@layer utilities` for modern CSS patterns
4. Add container queries utilities
5. Integrate with existing Tailwind setup

**Estimated:** 2-3 hours

### Phase 3: duet-company/apps/frontend (New)

**Tasks:**
1. Setup Next.js 14 with modern CSS
2. Integrate Oat CSS framework
3. Add modern CSS layer on top
4. Create component patterns with `@scope`
5. Build semantic HTML components
6. Setup TypeScript types for custom properties

**Estimated:** 4-5 hours

---

## Resources

- [Modern CSS Code Snippets](https://modern-css.com/) - Full reference
- [Oat UI Library](https://oat.ink/) - Semantic HTML framework
- [MDN CSS Nesting](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Nesting_selector)
- [Can I Use](https://caniuse.com/) - Browser support checker
- [OKLCH Color Picker](https://oklch.com/) - Perceptually uniform colors

---

**Next Steps:** Start with Phase 1 - Convert color system to OKLCH
