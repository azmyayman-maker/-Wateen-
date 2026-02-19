# Ticket 3.1: Next.js Boilerplate & RTL Foundation

## Ticket Metadata

| Field | Value |
|-------|-------|
| **ID** | 3.1 |
| **Title** | Next.js Boilerplate & RTL Foundation |
| **Status** | Completed |
| **Date** | 2026-02-19 |
| **Assignee** | Antigravity |

---

## Executive Summary

The frontend foundation for the Wateen Healthcare Platform was successfully built using **Next.js 16** with the App Router architecture, configured specifically for Arabic (RTL) users with a medical-grade aesthetic. The implementation establishes a production-ready scaffold with proper RTL direction, Arabic typography via the Cairo font family, and a medical "Teal/Blue" color palette. Route groups have been established to separate authentication flows from dashboard views, supporting the project's modular monolith architecture at the folder level.

---

## File Manifest

### Core Configuration Files

| File | Purpose |
|------|---------|
| [`frontend/src/app/layout.tsx`](../../frontend/src/app/layout.tsx) | Root layout with RTL direction (`dir="rtl"`), Arabic language attribute (`lang="ar"`), and Cairo font configuration |
| [`frontend/src/app/globals.css`](../../frontend/src/app/globals.css) | Global styles with CSS custom properties for the medical Teal/Blue color palette and Arabic typography settings |
| [`frontend/package.json`](../../frontend/package.json) | Project dependencies including Next.js 16, React 19, Tailwind CSS v4, and TypeScript 5 |

### Route Group Scaffolds

| File | Purpose |
|------|---------|
| [`frontend/src/app/(auth)/layout.tsx`](../../frontend/src/app/(auth)/layout.tsx) | Shared layout for authentication pages with centered card container |
| [`frontend/src/app/(auth)/login/page.tsx`](../../frontend/src/app/(auth)/login/page.tsx) | Login page scaffold with Arabic labels and form elements |
| [`frontend/src/app/(auth)/register/page.tsx`](../../frontend/src/app/(auth)/register/page.tsx) | Registration page scaffold |
| [`frontend/src/app/(dashboard)/layout.tsx`](../../frontend/src/app/(dashboard)/layout.tsx) | Shared layout for dashboard pages with header navigation |
| [`frontend/src/app/(dashboard)/patient/page.tsx`](../../frontend/src/app/(dashboard)/patient/page.tsx) | Patient dashboard scaffold with metric cards |
| [`frontend/src/app/(dashboard)/nurse/page.tsx`](../../frontend/src/app/(dashboard)/nurse/page.tsx) | Nurse dashboard scaffold |

### Shared Components

| File | Purpose |
|------|---------|
| [`frontend/src/components/shared/Button.tsx`](../../frontend/src/components/shared/Button.tsx) | Reusable button component with variant support |
| [`frontend/src/components/shared/Input.tsx`](../../frontend/src/components/shared/Input.tsx) | Reusable input component with Arabic label support |
| [`frontend/src/components/shared/Card.tsx`](../../frontend/src/components/shared/Card.tsx) | Reusable card container component |

---

## Configuration & Environment

### RTL Configuration

The root layout in [`frontend/src/app/layout.tsx`](../../frontend/src/app/layout.tsx:22) establishes RTL direction at the document level:

```tsx
<html lang="ar" dir="rtl" className={cairo.variable}>
```

This configuration ensures:
- **`lang="ar"`** — Sets the document language for screen readers and search engines
- **`dir="rtl"`** — Enables right-to-left text direction for the entire application
- **`className={cairo.variable}`** — Applies the Cairo font CSS variable for global typography

### Cairo Font Integration

The Cairo font is configured in [`frontend/src/app/layout.tsx`](../../frontend/src/app/layout.tsx:5) using `next/font/google`:

```tsx
const cairo = Cairo({
  subsets: ["arabic", "latin"],
  display: "swap",
  variable: "--font-cairo",
});
```

Key settings:
- **`subsets: ["arabic", "latin"]`** — Loads both Arabic and Latin character sets
- **`display: "swap"`** — Ensures text remains visible during font loading (FOUT mitigation)
- **`variable: "--font-cairo"`** — Creates a CSS custom property for Tailwind integration

The font is then referenced in [`globals.css`](../../frontend/src/app/globals.css:36):

```css
--font-sans: var(--font-cairo), 'Cairo', 'Amiri', 'Noto Sans Arabic', sans-serif;
```

### Medical Color Palette

The theme uses a medical-grade Teal/Blue palette defined in [`globals.css`](../../frontend/src/app/globals.css:3):

| Variable | RGB Value | Usage |
|----------|-----------|-------|
| `--primary` | `8 145 178` | Primary teal for buttons, links, accents |
| `--primary-light` | `34 211 238` | Lighter teal for hover states |
| `--secondary` | `20 184 166` | Secondary accent color |
| `--success` | `16 185 129` | Success states and confirmations |
| `--warning` | `245 158 11` | Warning indicators |
| `--error` | `239 68 68` | Error states and destructive actions |

### Accessibility Features

- **Skip Link**: A skip-to-content link is implemented in the root layout for keyboard navigation:
  ```tsx
  <a href="#main-content" className="skip-link">
    تخطي إلى المحتوى الرئيسي
  </a>
  ```
- **Focus Indicators**: Custom focus styles defined in [`globals.css`](../../frontend/src/app/globals.css:49):
  ```css
  :focus-visible {
    outline: 2px solid rgb(var(--primary));
    outline-offset: 2px;
  }
  ```
- **WCAG 2.1 AA Target**: All components designed with accessibility compliance in mind

---

## Verification Steps

### Running the Development Server

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`.

### Manual Verification Checklist

1. **RTL Behavior**
   - Open `http://localhost:3000` in a browser
   - Verify text aligns right-to-left
   - Check that the browser's direction indicator shows "RTL" in developer tools

2. **Font Loading**
   - Open Developer Tools → Network → Filter by "Font"
   - Verify Cairo font files are loaded
   - Check that Arabic text renders with the Cairo typeface

3. **Route Groups**
   - Navigate to `http://localhost:3000/login` — should display the login page
   - Navigate to `http://localhost:3000/register` — should display the registration page
   - Navigate to `http://localhost:3000/patient` — should display the patient dashboard
   - Navigate to `http://localhost:3000/nurse` — should display the nurse dashboard

4. **Color Palette**
   - Inspect elements to verify CSS custom properties are applied
   - Check that primary buttons use the teal color (`rgb(8 145 178)`)

5. **Accessibility**
   - Press `Tab` key to verify focus indicators are visible
   - Test the skip link by pressing `Tab` on page load

---

## Architectural Compliance

### Route Groups for Domain Separation

The implementation uses Next.js **Route Groups** to support the project's modular architecture:

```
src/app/
├── (auth)/           # Authentication domain
│   ├── layout.tsx    # Shared auth layout
│   ├── login/
│   └── register/
└── (dashboard)/      # Dashboard domain
    ├── layout.tsx    # Shared dashboard layout
    ├── patient/
    └── nurse/
```

**Benefits of this approach:**

1. **Domain Isolation** — Each route group encapsulates its own layout and pages, preventing cross-domain coupling at the folder level.

2. **URL Cleanliness** — Route groups don't affect the URL structure (`(auth)/login` maps to `/login`, not `/auth/login`).

3. **Layout Composition** — Each domain can define its own layout without affecting others. The auth layout uses a centered card, while the dashboard layout includes a header navigation.

4. **Scalability** — New domains (e.g., `(admin)`, `(api-docs)`) can be added without restructuring existing code.

5. **Modular Monolith Alignment** — This folder structure mirrors the backend's modular approach, where each Django app handles a specific domain concern.

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Largest Contentful Paint (LCP) | < 2.5s | Configured |
| First Input Delay (FID) | < 100ms | Configured |
| Cumulative Layout Shift (CLS) | < 0.1 | Configured |
| Font Display | `swap` | Implemented |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.1.6 | React framework with App Router |
| `react` | 19.2.3 | UI library |
| `tailwindcss` | ^4.0 | Utility-first CSS framework |
| `typescript` | ^5.0 | Type safety |
| `clsx` | ^2.1.1 | Conditional class names |
| `tailwind-merge` | ^3.5.0 | Merge Tailwind classes |

---

## Next Steps

This ticket establishes the frontend foundation. Subsequent tickets will build upon this scaffold to implement:

- Backend API integration
- Authentication flow with JWT tokens
- Real-time features via WebSocket
- Geospatial visit scheduling
