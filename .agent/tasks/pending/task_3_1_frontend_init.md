# Task: Frontend Initialization (Ticket 3.1)

## 1. Context & Objective

Initialize the frontend for the Wateen Healthcare Platform. We need a modern, performant foundation using Next.js 14, strictly configured for RTL (Arabic) support from day one.

## 2. Technical Specifications

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **RTL Support:** Mandatory (`dir="rtl"` in root layout)
- **Root Directory:** `frontend` (create this folder in the project root)

## 3. Implementation Steps

1.  **Initialize Project:**
    - Execute: `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-git` inside the project root (d:\projects\Wateen).
    - Note: Ensure you are in `d:\projects\Wateen` before running this.
2.  **RTL Configuration (`frontend/src/app/layout.tsx`):**
    - Update the Root Layout to use `<html lang="ar" dir="rtl">`.
    - Import and configure the `Cairo` font from `next/font/google` and apply it to the body.
3.  **Folder Scaffolding:**
    - Create `frontend/src/app/(auth)/login/page.tsx` (Export default function LoginPage...)
    - Create `frontend/src/app/(auth)/register/page.tsx` (Export default function RegisterPage...)
    - Create `frontend/src/app/(dashboard)/patient/page.tsx` (Export default function PatientDashboard...)
    - Create `frontend/src/app/(dashboard)/nurse/page.tsx` (Export default function NurseDashboard...)
    - Create directory `frontend/src/components/shared/`
4.  **Verification Page (`frontend/src/app/page.tsx`):**
    - Update the main page to display a large centered heading: "مرحباً بكم في وتين - Wateen".
    - Ensure it uses Tailwind classes for styling (e.g., `text-4xl font-bold text-center mt-20`).

## 4. Acceptance Criteria

- [ ] `frontend` folder exists.
- [ ] `npm run build` passes within `frontend`.
- [ ] `src/app/layout.tsx` contains `dir="rtl"`.
- [ ] Route groups `(auth)` and `(dashboard)` exist with page files.
