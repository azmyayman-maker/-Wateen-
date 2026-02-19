# Data Model: Frontend Initialization

**Feature**: 004-frontend-init | **Date**: 2026-02-19

## Component Hierarchy

### Root Layout

```
RootLayout
├── Cairo Font Provider
├── HTML (lang="ar", dir="rtl")
└── Body
    └── {children}
```

### Route Groups

```
app/
├── layout.tsx          # Root layout - RTL, Cairo font, theme
├── page.tsx            # Homepage - welcome message
├── (auth)/
│   ├── layout.tsx      # Auth layout - centered card wrapper
│   ├── login/page.tsx  # Login form placeholder
│   └── register/page.tsx # Register form placeholder
└── (dashboard)/
    ├── layout.tsx      # Dashboard layout - navigation wrapper
    ├── patient/page.tsx # Patient dashboard placeholder
    └── nurse/page.tsx  # Nurse dashboard placeholder
```

## Component Specifications

### 1. Root Layout (`app/layout.tsx`)

| Property | Value |
|----------|-------|
| Purpose | Global RTL configuration, font loading, theme CSS variables |
| Props | `{ children: ReactNode }` |
| Output | HTML document with Cairo font, RTL direction |

**Key Implementation**:
- Import Cairo from `next/font/google`
- Apply font variable to body className
- Set `lang="ar"` and `dir="rtl"` on html element
- Define CSS custom properties for theme colors

### 2. Auth Layout (`app/(auth)/layout.tsx`)

| Property | Value |
|----------|-------|
| Purpose | Shared layout for authentication pages |
| Props | `{ children: ReactNode }` |
| Output | Centered card container with max-width |

**Key Implementation**:
- Flexbox centering with `min-h-screen`
- Card wrapper with padding and shadow
- Consistent spacing for form elements

### 3. Dashboard Layout (`app/(dashboard)/layout.tsx`)

| Property | Value |
|----------|-------|
| Purpose | Shared layout for dashboard pages |
| Props | `{ children: ReactNode }` |
| Output | Container with future navigation slot |

**Key Implementation**:
- Responsive container with padding
- Slot for future sidebar/navigation
- Content area with scroll

### 4. Shared Components

#### Button (`components/shared/Button.tsx`)

| Property | Type | Default |
|----------|------|---------|
| variant | 'primary' \| 'secondary' \| 'ghost' | 'primary' |
| size | 'sm' \| 'md' \| 'lg' | 'md' |
| disabled | boolean | false |
| loading | boolean | false |
| children | ReactNode | required |

**Accessibility**:
- Focus visible ring
- ARIA disabled state
- Loading spinner with `aria-busy`

#### Input (`components/shared/Input.tsx`)

| Property | Type | Default |
|----------|------|---------|
| type | 'text' \| 'email' \| 'password' | 'text' |
| label | string | required |
| error | string \| undefined | undefined |
| disabled | boolean | false |

**Accessibility**:
- Label associated with input via `htmlFor`
- Error message linked via `aria-describedby`
- Required indicator with `aria-required`

#### Card (`components/shared/Card.tsx`)

| Property | Type | Default |
|----------|------|---------|
| variant | 'elevated' \| 'outlined' | 'elevated' |
| padding | 'sm' \| 'md' \| 'lg' | 'md' |
| children | ReactNode | required |

## CSS Variables Schema

```css
:root {
  /* Colors */
  --primary: 8 145 178;           /* Cyan-600 RGB */
  --primary-light: 34 211 238;    /* Cyan-400 RGB */
  --secondary: 20 184 166;        /* Teal-500 RGB */
  --background: 255 255 255;      /* White RGB */
  --surface: 248 250 252;         /* Slate-50 RGB */
  --text-primary: 15 23 42;       /* Slate-900 RGB */
  --text-secondary: 71 85 105;    /* Slate-600 RGB */
  --border: 226 232 240;          /* Slate-200 RGB */
  --success: 16 185 129;          /* Emerald-500 RGB */
  --warning: 245 158 11;          /* Amber-500 RGB */
  --error: 239 68 68;             /* Red-500 RGB */
  
  /* Typography */
  --font-cairo: 'Cairo', sans-serif;
  --line-height: 1.8;
  
  /* Spacing */
  --container-max: 1280px;
  --card-max: 480px;
  
  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

## Tailwind Configuration Schema

```typescript
// tailwind.config.ts
const config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-cairo)', 'sans-serif'],
      },
      colors: {
        primary: 'rgb(var(--primary) / <alpha-value>)',
        secondary: 'rgb(var(--secondary) / <alpha-value>)',
        surface: 'rgb(var(--surface) / <alpha-value>)',
      },
      lineHeight: {
        arabic: 'var(--line-height)',
      },
    },
  },
  plugins: [],
}
```

## State Transitions

N/A - No client state required for initialization phase.

## Validation Rules

### Form Validation (Future)

| Field | Rules | Error Message (Arabic) |
|-------|-------|------------------------|
| email | Required, valid email format | البريد الإلكتروني غير صالح |
| password | Required, min 8 characters | كلمة المرور يجب أن تكون 8 أحرف على الأقل |

### Accessibility Validation

| Check | Tool | Threshold |
|-------|------|-----------|
| Contrast Ratio | axe-core | ≥ 4.5:1 |
| Focus Order | Manual | Logical tab order |
| ARIA Labels | axe-core | No violations |
| Heading Hierarchy | axe-core | Proper nesting |
