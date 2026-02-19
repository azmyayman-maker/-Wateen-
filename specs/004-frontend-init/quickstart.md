# Quickstart: Frontend Initialization

**Feature**: 004-frontend-init | **Date**: 2026-02-19

## Prerequisites

- Node.js 18.17 or later
- npm 9.0 or later
- Git (for version control)

## Quick Setup

```bash
# 1. Initialize Next.js project
cd D:/projects/Wateen
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-git

# 2. Navigate to frontend
cd frontend

# 3. Install additional dependencies
npm install --save-dev @axe-core/react jest-axe @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom @playwright/test
```

## Development Workflow

```bash
# Start development server
npm run dev
# Opens at http://localhost:3000

# Run linting
npm run lint

# Run type checking
npx tsc --noEmit

# Run tests
npm test

# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout (EDIT: add RTL + Cairo)
│   │   ├── page.tsx           # Homepage (EDIT: add welcome message)
│   │   ├── globals.css        # Global styles (EDIT: add CSS variables)
│   │   ├── (auth)/            # CREATE
│   │   │   ├── layout.tsx
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   └── (dashboard)/       # CREATE
│   │       ├── layout.tsx
│   │       ├── patient/page.tsx
│   │       └── nurse/page.tsx
│   └── components/
│       └── shared/            # CREATE
│           ├── Button.tsx
│           ├── Input.tsx
│           └── Card.tsx
├── package.json
└── (tailwind.config.ts removed in v4)
```

## Key Implementation Steps

### Step 1: Configure Root Layout

Edit `src/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import { Cairo } from "next/font/google";
import "./globals.css";

const cairo = Cairo({
  subsets: ["arabic", "latin"],
  display: "swap",
  variable: "--font-cairo",
});

export const metadata: Metadata = {
  title: "وتين - Wateen Healthcare Platform",
  description: "منصة وتين للرعاية الصحية",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl" className={cairo.variable}>
      <body className="font-sans bg-background text-text-primary">
        {children}
      </body>
    </html>
  );
}
```

### Step 2: Add Global CSS Variables

Edit `src/app/globals.css`:

```css
@import "tailwindcss";

:root {
  --primary: 8 145 178;
  --primary-light: 34 211 238;
  --secondary: 20 184 166;
  --background: 255 255 255;
  --surface: 248 250 252;
  --text-primary: 15 23 42;
  --text-secondary: 71 85 105;
  --border: 226 232 240;
  --success: 16 185 129;
  --warning: 245 158 11;
  --error: 239 68 68;
  --line-height: 1.8;
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg:
    0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

@theme inline {
  --color-primary: rgb(var(--primary) / <alpha-value>);
  --color-primary-light: rgb(var(--primary-light) / <alpha-value>);
  --color-secondary: rgb(var(--secondary) / <alpha-value>);
  --color-background: rgb(var(--background) / <alpha-value>);
  --color-surface: rgb(var(--surface) / <alpha-value>);
  --color-text-primary: rgb(var(--text-primary) / <alpha-value>);
  --color-text-secondary: rgb(var(--text-secondary) / <alpha-value>);
  --color-border: rgb(var(--border) / <alpha-value>);
  --color-success: rgb(var(--success) / <alpha-value>);
  --color-warning: rgb(var(--warning) / <alpha-value>);
  --color-error: rgb(var(--error) / <alpha-value>);
  --font-sans:
    var(--font-cairo), "Cairo", "Amiri", "Noto Sans Arabic", sans-serif;
  --line-height-arabic: var(--line-height);
  --radius-sm-base: 0.25rem;
  --radius-md-base: 0.5rem;
  --radius-lg-base: 1rem;
}

body {
  background: rgb(var(--background));
  color: rgb(var(--text-primary));
  line-height: var(--line-height);
}
```

### Step 3: Update Homepage

Edit `src/app/page.tsx`:

```tsx
export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <h1 className="text-4xl font-bold text-center text-primary">
        مرحباً بكم في وتين - Wateen
      </h1>
    </main>
  );
}
```

### Step 4: Create Route Groups

Create auth routes:

```bash
mkdir -p src/app/\(auth\)/login
mkdir -p src/app/\(auth\)/register
mkdir -p src/app/\(dashboard\)/patient
mkdir -p src/app/\(dashboard\)/nurse
```

### Step 5: Configure Tailwind v4 Theme

Tailwind v4 moves configuration from `tailwind.config.ts` to CSS variables in `src/app/globals.css` using the `@theme` directive.

Ensure your `src/app/globals.css` includes the `@theme inline` block as shown in **Step 2**. This replaces the need for a separate `tailwind.config.ts` file for these theme extensions.

**Note:** If `tailwind.config.ts` was created by the init script, you can delete it if you are fully using the CSS-first configuration, or keep it minimal if you need specific plugin configurations that aren't yet supported in CSS.

The `@theme` block in `globals.css` should look like this (already added in Step 2):

```css
@theme inline {
  --color-primary: rgb(var(--primary) / <alpha-value>);
  /* ... other colors ... */
  --font-sans:
    var(--font-cairo), "Cairo", "Amiri", "Noto Sans Arabic", sans-serif;
}
```

## Verification Checklist

- [ ] `npm run build` passes with no errors
- [ ] Homepage displays "مرحباً بكم في وتين - Wateen" centered
- [ ] HTML element has `lang="ar"` and `dir="rtl"`
- [ ] Cairo font is loaded and applied
- [ ] `/login` route renders
- [ ] `/register` route renders
- [ ] `/patient` route renders
- [ ] `/nurse` route renders
- [ ] All pages display RTL correctly

## Common Issues

### Issue: Font not loading

**Solution**: Ensure `next/font/google` is imported correctly and font variable is applied to html element.

### Issue: RTL not applying

**Solution**: Verify `dir="rtl"` is on the `<html>` element, not body.

### Issue: Tailwind colors not working

**Solution**: Use RGB format in CSS variables and reference with `rgb(var(--name) / <alpha-value>)` in Tailwind config.

## Testing Commands

```bash
# Type check
npx tsc --noEmit

# Lint
npm run lint

# Build
npm run build

# Accessibility audit (after starting dev server)
npx lighthouse http://localhost:3000 --only-categories=accessibility --view
```

## Next Steps

After initialization:

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement shared components (Button, Input, Card)
3. Add form validation to auth pages
4. Build dashboard layouts with navigation
