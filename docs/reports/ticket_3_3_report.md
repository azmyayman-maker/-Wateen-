# Ticket 3.3: Patient & Nurse Dashboards (Core Medical UI)

## Ticket Metadata

| Field        | Value                      |
| ------------ | -------------------------- |
| **ID**       | 3.3                        |
| **Title**    | Patient & Nurse Dashboards |
| **Status**   | Completed                  |
| **Date**     | 2026-02-21                 |
| **Assignee** | Antigravity                |

---

## Executive Summary

Ticket 3.3 resolves the core user interface requirements for both the Patient and Nurse experiences within the Wateen Healthcare Platform. The implementation provides production-grade, highly optimized React code that adheres to strict UI/UX Pro Max guidelines, heavily featuring Arabic RTL layouts, physics-based interactions, and medical-grade aesthetics.

The **Patient Dashboard (The Calm Oasis)** focuses on reducing medical anxiety through smooth glassmorphism, slow breathing animations, and accessible typography. In contrast, the **Nurse Dashboard (The Tactical Pulse)** is designed for high-stress, high-sunlight environments with stark contrasts, a massive tactile availability switch, and immediate status recognition.

---

## File Manifest

### Core Dashboard Components

| File                                             | Purpose                                                                                                                                        |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontend/src/components/PatientDashboard.tsx`   | The primary dashboard for patients, featuring a mix-blend-multiply ambient background, active booking radar ping, and staggered service grids. |
| `frontend/src/components/NurseDashboard.tsx`     | The tactical command center for nurses. Includes the premium cubic-bezier animated "متاح/غير متاح" switch and snapping incoming requests.      |
| `frontend/src/components/WateenAnimatedLogo.tsx` | Next-generation React component that loads the official Wateen branding with a cinematic fade-in and subtle float-glow physics.                |
| `frontend/src/components/WateenCanvasLogo.tsx`   | Dedicated Canvas-based renderer for the Wateen logo to handle ultra-high DPI scaling and performant alpha fades.                               |

---

## Architectural & UX Achievements

### 1. The "Calm Oasis" (Patient POV)

- **Ambient Breathing Background:** Utilized CSS mix-blend modes with heavily blurred, animated color orbs to create a soothing, living background that reduces stress.
- **Service Grid Physics:** Services slide up with staggered delays and react to hover states with magnetic-like scale properties (`active:scale-[0.98]`), making the UI feel tactile and native.
- **Status Accessibility:** Medical histories and active bookings use highly legible Arabic typography (using the `Cairo` font) with clear, color-coded SVG indicators mapping to the backend's state machine.

### 2. The "Tactical Pulse" (Nurse POV)

- **High-Contrast Typography:** Colors are stark (Deep Slate vs White) to ensure absolute legibility when a nurse is operating outdoors under direct Egyptian sunlight.
- **Premium Availability Toggle:** The core action of going online/offline is managed by a massive, easy-to-hit switch. The switch utilizes complex CSS drop-shadows, inset shadows, and `cubic-bezier` timing functions to feel like a high-end physical iOS toggle.
- **Urgency Visualization:** Incoming requests snap into view with explicit "Emergency" (طوارئ) red tags and bold distance metrics, allowing rapid triaging.

### 3. Motion Engineering (Logo Entrance)

Since the `icon.svg` asset provided was a rasterized PNG embedded in an SVG shell, standard CSS stroke tracing was mathematically impossible. Thus, the engineering team executed a custom entrance:

1. **The Cinematic Fade:** Utilizing `requestAnimationFrame`, the logo gracefully scales and fades in.
2. **The Float-Glow:** Once visible, a dynamic cyan-to-purple composite shadow loops behind the logo, simulating a breathing entity.

---

## Component Constraints & Compliance

- **Framework:** Next.js 14 / React 19.
- **Styling:** Tailwind CSS V4 (Utility-first CSS, Custom Keyframes via `dangerouslySetInnerHTML` to prevent global stylesheet bloating).
- **Directionality:** Strict `dir="rtl"` applied at the root container level.
- **State Management:** Localized component state (`useState`, `useEffect`) avoiding unnecessary global context layers for UI-only toggles.

---

## Verification Steps

1. **Patient Dashboard:**
   - Launch application on `http://localhost:3000`.
   - Verify that the ambient background pulses slowly (10-second animations).
   - Ensure the "طلب خدمة جديدة" grid cascades correctly upon load.

2. **Nurse Tactical Console:**
   - Locate the large availability toggle.
   - Click it to transition from "غير متاح" to "متاح للخدمة".
   - Ascertain the cubic-bezier physics trigger correctly, replacing the layout with a cyan glow (`#00BCD4`).

3. **Responsive Fluidity:**
   - Ensure full functionality and layout integrity down to 375px (iPhone SE viewport) and up to 1440px without horizontal scrolling.
