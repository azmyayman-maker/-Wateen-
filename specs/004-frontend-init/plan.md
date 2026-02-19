# Implementation Plan: Frontend Initialization

**Branch**: `004-frontend-init` | **Date**: 2026-02-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-init/spec.md`

## Summary

Initialize a modern Next.js 14 frontend for the Wateen Healthcare Platform with RTL Arabic support, Cairo font, and a light medical-themed design system. The foundation supports authentication pages and role-based dashboards with WCAG 2.1 AA accessibility and optimized Core Web Vitals.

## Technical Context

**Language/Version**: TypeScript 5.x / Next.js 14 (App Router)
**Primary Dependencies**: Next.js 14, React 18, Tailwind CSS, next/font (Cairo), ESLint
**Storage**: N/A (frontend only, no data persistence)
**Testing**: Jest, React Testing Library, Playwright (E2E)
**Target Platform**: Web (modern browsers, mobile-responsive)
**Project Type**: Web application (frontend)
**Performance Goals**: LCP < 2.5s, FID < 100ms, CLS < 0.1 (Core Web Vitals "Good")
**Constraints**: RTL-first design, Arabic as primary language, WCAG 2.1 AA compliance, no JavaScript required for basic rendering
**Scale/Scope**: 5 initial routes, healthcare platform foundation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution template is not yet populated for this project. Proceeding with standard best practices:
- ✅ Test-first approach planned
- ✅ Observability via Lighthouse/Core Web Vitals
- ✅ Simplicity: minimal initial feature set
- ✅ TypeScript for type safety

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-init/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (component hierarchy)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - no API)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout (RTL, Cairo font)
│   │   ├── page.tsx             # Homepage
│   │   ├── globals.css          # Tailwind + custom CSS variables
│   │   ├── (auth)/
│   │   │   ├── layout.tsx       # Auth layout wrapper
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   └── (dashboard)/
│   │       ├── layout.tsx       # Dashboard layout wrapper
│   │       ├── patient/
│   │       │   └── page.tsx
│   │       └── nurse/
│   │           └── page.tsx
│   ├── components/
│   │   └── shared/              # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       └── index.ts
│   └── lib/
│       └── utils.ts             # Utility functions (cn, etc.)
├── public/
│   └── fonts/                   # Optional: local font fallbacks
├── tailwind.config.ts           # RTL-aware config
├── next.config.js               # Next.js configuration
├── tsconfig.json                # TypeScript config
├── package.json
└── jest.config.js               # Testing config
```

**Structure Decision**: Web application with frontend/ directory. Route groups `(auth)` and `(dashboard)` provide logical separation without affecting URL structure. Shared components directory enables design system consistency.

## Design System

### Color Palette (Healthcare Light Theme)

| Token | Light Mode | Usage |
|-------|-----------|-------|
| `--primary` | #0891B2 (Cyan-600) | Primary actions, links |
| `--primary-light` | #22D3EE (Cyan-400) | Hover states |
| `--secondary` | #14B8A6 (Teal-500) | Secondary actions |
| `--background` | #FFFFFF | Page background |
| `--surface` | #F8FAFC (Slate-50) | Cards, elevated surfaces |
| `--text-primary` | #0F172A (Slate-900) | Primary text |
| `--text-secondary` | #475569 (Slate-600) | Secondary text |
| `--border` | #E2E8F0 (Slate-200) | Borders, dividers |
| `--success` | #10B981 (Emerald-500) | Success states |
| `--warning` | #F59E0B (Amber-500) | Warning states |
| `--error` | #EF4444 (Red-500) | Error states |

### Typography

| Token | Font | Size | Weight |
|-------|------|------|--------|
| `--font-display` | Cairo | 2.25rem (36px) | 700 |
| `--font-heading` | Cairo | 1.5rem (24px) | 600 |
| `--font-body` | Cairo | 1rem (16px) | 400 |
| `--font-small` | Cairo | 0.875rem (14px) | 400 |

### Spacing Scale

Tailwind default spacing with RTL-aware logical properties (start/end instead of left/right).

## Accessibility Requirements

- WCAG 2.1 Level AA compliance
- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
- All interactive elements focusable via keyboard
- ARIA labels for icons and interactive elements
- Skip-to-content link on all pages
- Proper heading hierarchy (h1 → h2 → h3)
- Form labels associated with inputs
- Error messages announced to screen readers

## Performance Optimizations

Based on Vercel React Best Practices:

1. **Bundle Size**: Dynamic imports for route components
2. **Font Loading**: `next/font` with `display: swap` for Cairo
3. **CSS**: Tailwind purging unused styles
4. **Images**: Next.js Image component with lazy loading
5. **Parallel Fetching**: Structure components for parallel data fetching (future)

## Complexity Tracking

No constitution violations. Standard web application structure with appropriate separation of concerns.
