# Ticket 3.4: Interactive Spatial UI & Live Tracking

## Ticket Metadata

| Field        | Value                                        |
| ------------ | -------------------------------------------- |
| **ID**       | 3.4                                          |
| **Title**    | Patient Location Picker & Nurse Live Tracker |
| **Status**   | Completed                                    |
| **Date**     | 2026-02-21                                   |
| **Assignee** | Antigravity                                  |

---

## Executive Summary

Ticket 3.4 introduces advanced Spatial and Geolocation UI elements to the Wateen Platform. Recognizing that standard static map images or default generic interfaces fail to deliver the expected premium experience, the platform now integrates **The Living Map** for Patients and **The Pulse Radar** for Nurses.

These components are engineered utilizing high-performance CSS animations (Sonar Ping, Breathing Location Pins), localized Arabic typography, and ergonomic physical layout designs. The result is a tactile, responsive geographical interface tailored strictly for mobile viewport interaction in the field.

---

## File Manifest

| File                                                | Purpose                                                                                                                                                                                                                           |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontend/src/components/PatientLocationPicker.tsx` | Allows the patient to seamlessly adjust their requested service location. Includes a breathing central pin and a soft-matte bottom action sheet for confirmation.                                                                 |
| `frontend/src/components/NurseLiveTracker.tsx`      | Provides the nurse with an active, real-time tracking interface showing their ETA and the patient's destination. It houses the "Pulse Radar" animation and an anti-bottom-sheet 'Floating Command Island' for navigation actions. |

---

## Architectural & UX Achievements

### 1. The "Living Map" (Patient Location Picker)

- **Breathing Center Pin:** An absolute-centered vector map pin drops a dynamic multi-layered shadow that pulses to draw the user's eye to the exact crosshair location without moving the map view itself unnecessarily.
- **Glass Action Sheet:** A fixed bottom drawer utilizes pure CSS `backdrop-blur` and a transparent slate background (`bg-slate-900/90`) to maintain map visibility underneath while ensuring critical actions ("تأكيد الموقع الحالي") remain entirely accessible and legible.
- **Micro-Interaction Physics:** Buttons employ heavy localized `active:scale-95` and offset shadowing to emulate physical depth.

### 2. The "Pulse Radar" (Nurse Live Tracker)

- **Sonar Ping Animation:** To communicate "live tracking" without expensive canvas rerenders, the nurse's positional marker generates expanding CSS rings (`animate-ping`) that dynamically fade via opacity scaling.
- **Floating Command Island:** Avoiding the cliché and screen-heavy full bottom sheet, navigation actions (e.g., "بدء الملاحة") reside in a floating pill-shaped container that hovers gracefully above the map. This design maximizes the geospatial viewable area.
- **Urgent Shield Indicator:** Integrated safely in the top-right corner is a visual `Safe Visit` shield that visualizes ambient microphone levels (simulating the Blackbox features from Phase 8) through animated equalizer bars.
- **Circular SVG ETA:** Replaced standard text ETAs with a visual ring progress indicator overlaying the destination avatar, communicating time-to-arrival purely visually.

---

## Technical Considerations

- **Simulated Map Layer:** Due to the staging nature of the components, the actual `react-leaflet` or `mapbox-gl` instances are mocked gracefully via grid intersecting backgrounds. This allows UI logic validation before committing to expensive third-party token integrations.
- **RTL & LTR Geospatial Constraints:** Great care was taken to ensure that Floating Action Buttons (FABs) scale correctly for RTL. For example, the `right-0` / `left-0` CSS bindings were carefully audited to not mirror map controls incorrectly.
- **Z-Index Layering:** Strict semantic z-index strategies (`z-10`, `z-20`, `z-50`) were engineered to ensure the floating islands never intersect or clip beneath the map engine's own internal UI controls.

---

## Verification Steps

1. **Patient Location Picker:**
   - Mount the `PatientLocationPicker` component.
   - Verify the center pin breathes (animation runs infinitely).
   - Ensure the large black confirmation button spans the device width minus padding.

2. **Nurse Live Tracking:**
   - Mount the `NurseLiveTracker` component.
   - Assess the custom avatar's Sonar Radar animation. Does it ping seamlessly without clipping?
   - Verify the safety equalizer bars in the top left/right corner animate up and down randomly using discrete animation delays.

3. **General UI Compliance:**
   - Verify the layout complies with mobile-first rendering (using standard Tailwind arbitrary values if required).
   - Confirm all texts are perfectly aligned Right-to-Left.
