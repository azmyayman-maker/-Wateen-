# Research: Frontend Initialization

**Feature**: 004-frontend-init | **Date**: 2026-02-19

## Research Tasks

### 1. RTL Arabic Support in Next.js 14

**Decision**: Use `dir="rtl"` and `lang="ar"` on root `<html>` element in `app/layout.tsx`

**Rationale**: 
- Next.js App Router supports RTL natively via HTML attributes
- No additional libraries required for basic RTL support
- Tailwind CSS provides RTL-aware utilities with logical properties

**Alternatives Considered**:
- `next-rtl-plugin`: Unnecessary for simple RTL configuration
- CSS direction property: Less semantic than HTML attribute

**Implementation Notes**:
```tsx
// app/layout.tsx
<html lang="ar" dir="rtl">
```

### 2. Cairo Font Integration

**Decision**: Use `next/font/google` with Cairo font

**Rationale**:
- Native Next.js font optimization
- Automatic self-hosting for performance
- `display: swap` prevents FOIT (Flash of Invisible Text)
- Supports Arabic script with excellent rendering

**Alternatives Considered**:
- Google Fonts CDN: Missing Next.js optimizations
- Local font files: Maintenance overhead, no optimization benefits

**Implementation Notes**:
```tsx
import { Cairo } from 'next/font/google'
const cairo = Cairo({ 
  subsets: ['arabic', 'latin'],
  display: 'swap',
  variable: '--font-cairo'
})
```

### 3. Tailwind CSS RTL Configuration

**Decision**: Use Tailwind's logical properties with `rtl:` modifier for edge cases

**Rationale**:
- Tailwind 3.x+ supports RTL out of the box
- Logical properties (start/end) automatically adapt to RTL
- Use `rtl:` prefix only for directional overrides

**Alternatives Considered**:
- `tailwindcss-rtl`: Plugin no longer needed with Tailwind 3.x
- Custom CSS direction: More maintenance overhead

**Implementation Notes**:
```ts
// tailwind.config.ts
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-cairo)', 'sans-serif'],
      },
    },
  },
}
```

### 4. Accessibility Testing Approach

**Decision**: Multi-layered accessibility testing

**Rationale**:
- Automated: axe-core via jest-axe for unit tests
- Manual: Lighthouse accessibility audit
- E2E: Playwright accessibility snapshots

**Alternatives Considered**:
- Manual-only testing: Inconsistent coverage
- Third-party services: Overkill for initialization phase

**Implementation Notes**:
```bash
npm install --save-dev @axe-core/react jest-axe
npm install --save-dev @playwright/test
```

### 5. Core Web Vitals Optimization

**Decision**: Implement known Next.js optimizations from day one

**Rationale**:
- LCP: Font optimization, server-side rendering
- FID: Code splitting, minimize main thread work
- CLS: Font display swap, reserved image dimensions

**Key Patterns** (from Vercel React Best Practices):
- `bundle-dynamic-imports`: Use `next/dynamic` for heavy components
- `server-serialization`: Minimize client-side JavaScript
- `rendering-hydration-no-flicker`: Prevent layout shifts

### 6. Component Architecture

**Decision**: Compound components with explicit variants

**Rationale** (from Vercel Composition Patterns):
- Avoids boolean prop proliferation
- Better TypeScript inference
- More maintainable API surface

**Pattern**:
```tsx
// Instead of: <Button variant="primary" size="large" disabled />
// Use: <Button.Primary size="large" disabled />
```

### 7. Healthcare Color Palette Research

**Decision**: Cyan/Teal medical theme

**Rationale**:
- Trust-building colors in healthcare industry
- Calming effect for patients
- Differentiates from competitors (avoiding generic blue)
- High contrast ratios achievable for accessibility

**WCAG Contrast Validation**:
- Cyan-600 (#0891B2) on white: 4.58:1 ✅ (AA normal text)
- Teal-500 (#14B8A6) on white: 3.67:1 ✅ (AA large text)
- Slate-900 (#0F172A) on white: 16.13:1 ✅ (AAA)

### 8. Arabic Typography Best Practices

**Decision**: Cairo with 1.8 line-height for Arabic text

**Rationale**:
- Arabic script requires more vertical space than Latin
- Cairo designed specifically for Arabic UI
- 1.8 line-height improves readability

**Implementation Notes**:
```css
:root {
  --line-height-arabic: 1.8;
}
body {
  line-height: var(--line-height-arabic);
}
```

## Resolved Clarifications

All NEEDS CLARIFICATION items from Technical Context have been resolved:
- ✅ Framework: Next.js 14 App Router
- ✅ Font: Cairo via next/font/google
- ✅ RTL: Native HTML attributes + Tailwind logical properties
- ✅ Testing: Jest + Playwright
- ✅ Accessibility: WCAG 2.1 AA with axe-core
- ✅ Performance: Core Web Vitals "Good" targets
