# Styling Guidelines for AiWhizPro

## Design Token System

Never hardcode the following—always use CSS variables from `frontend/assets/css/tokens.css`:

### Colors
```css
var(--primary)        /* Primary action/brand color */
var(--secondary)      /* Secondary accents */
var(--accent)         /* Highlight/focus states */
var(--background)     /* Page background */
var(--surface)        /* Card/container background */
var(--text-primary)   /* Primary text color */
var(--text-secondary) /* Secondary text color */
var(--border)         /* Border colors */
var(--error)          /* Error/danger state */
var(--success)        /* Success state */
var(--warning)        /* Warning state */
```

### Border Radius
```css
var(--radius-sm)      /* Small: 0.375rem (6px) */
var(--radius-md)      /* Medium: 0.5rem (8px) */
var(--radius-lg)      /* Large: 0.75rem (12px) */
var(--radius-xl)      /* Extra large: 1rem (16px) */
var(--radius-full)    /* Pill/circular: 9999px */
```

### Shadows
```css
var(--shadow-sm)      /* Small elevation */
var(--shadow-card)    /* Card/panel shadow */
var(--shadow-lg)      /* Large/prominent shadow */
var(--shadow-xl)      /* Extra large shadow */
```

### Typography
```css
var(--font-primary)   /* Primary font family */
var(--font-secondary) /* Secondary font family (monospace) */
var(--font-size-xs)   /* Small text: 0.75rem */
var(--font-size-sm)   /* Small: 0.875rem */
var(--font-size-base) /* Body: 1rem */
var(--font-size-lg)   /* Large: 1.125rem */
var(--font-size-xl)   /* Extra large: 1.25rem */
var(--font-size-2xl)  /* 2x large: 1.5rem */
var(--font-size-3xl)  /* 3x large: 1.875rem */
var(--font-size-4xl)  /* 4x large: 2.25rem */
var(--font-weight-normal)   /* 400 */
var(--font-weight-semibold) /* 600 */
var(--font-weight-bold)     /* 700 */
```

### Spacing
```css
var(--spacing-xs)     /* 0.25rem (4px) */
var(--spacing-sm)     /* 0.5rem (8px) */
var(--spacing-md)     /* 1rem (16px) */
var(--spacing-lg)     /* 1.5rem (24px) */
var(--spacing-xl)     /* 2rem (32px) */
var(--spacing-2xl)    /* 3rem (48px) */
```

## Template Guidelines

### ✅ DO: Use Tailwind Utilities + Design Tokens

```html
<!-- Good: Tailwind classes with token-aware colors -->
<button class="rounded-lg bg-primary px-4 py-2 text-white shadow-md hover:shadow-lg">
  Generate Post
</button>

<!-- Good: Using CSS variables for custom styling -->
<style>
.custom-section {
  color: var(--text-primary);
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
</style>
```

### ❌ DON'T: Hardcode Styling

```html
<!-- Bad: Hardcoded colors -->
<button class="rounded-8 bg-blue-600 px-4 py-2 text-white shadow-md">
  <!-- DON'T: hardcoded blue, radius value, shadow -->
</button>

<!-- Bad: Inline styles with hardcoded values -->
<div style="color: #333; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1)">
  <!-- DON'T: hardcoded hex colors, radius, shadow -->
</div>
```

## Component Patterns

### Cards (with tokens)
```html
<div class="rounded-[var(--radius-lg)] bg-[var(--surface)] p-6 shadow-[var(--shadow-card)]">
  <h3 class="text-[var(--font-size-lg)] font-[var(--font-weight-semibold)] text-[var(--text-primary)]">
    Title
  </h3>
  <p class="text-[var(--font-size-base)] text-[var(--text-secondary)]">Description</p>
</div>
```

### Buttons (with tokens)
```html
<!-- Primary button -->
<button class="rounded-[var(--radius-md)] bg-[var(--primary)] px-4 py-2 text-white hover:opacity-90">
  Action
</button>

<!-- Secondary button -->
<button class="rounded-[var(--radius-md)] border-2 border-[var(--border)] bg-[var(--surface)] text-[var(--text-primary)] hover:bg-[var(--background)]">
  Secondary
</button>
```

## Django Template Notes

- Use Django template variables for dynamic content
- Keep presentation logic in templates, business logic in views
- Link all stylesheets from `frontend/assets/css/` via `<link>` tags
- Never inline styles except for dynamic values (use `var()` instead)

## Review Checklist

When reviewing templates/styles:
- [ ] No hardcoded colors (check for `#RGB`, `rgb()`, color names)
- [ ] No hardcoded border-radius values (use `--radius-*`)
- [ ] No hardcoded shadows (use `--shadow-*`)
- [ ] No hardcoded font sizes (use `--font-size-*`)
- [ ] All text uses token colors (`--text-primary`, `--text-secondary`)
- [ ] Cards use `--shadow-card` or `--shadow-lg`
- [ ] Buttons use `--primary` or `--secondary` colors
- [ ] Spacing uses `--spacing-*` variables

---

**Reference**: [tokens.css](frontend/assets/css/tokens.css) — Source of truth for all design variables
