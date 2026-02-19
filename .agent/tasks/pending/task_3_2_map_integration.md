# Phase 3 - Ticket 3.2: Map Integration (React-Leaflet)

**CONTEXT:**
We are executing Phase 3, Ticket 3.2 of the Wateen Master Implementation Plan.
The goal is to integrate **React-Leaflet** into the Next.js 14 application while handling SSR constraints and ensuring RTL compatibility.

**CRITICAL CONSTRAINTS:**

1.  **SSR Handling:** Leaflet requires `window`. ALL map components MUST be imported using `next/dynamic` with `{ ssr: false }`.
2.  **Styling:** The map container MUST have a defined height (e.g., `h-[400px]` or `min-h-[400px]`) via Tailwind CSS.
3.  **Icons:** Fix `L.Icon.Default` image paths manually to avoid Webpack 5 asset issues.
4.  **RTL Support:** Ensure map controls are usable in RTL layout.

---

## 1. Dependency Installation

- [ ] Install required packages:
  ```bash
  npm install leaflet react-leaflet
  npm install -D @types/leaflet
  ```

## 2. Component Architecture

Create the following components in `src/components/maps/`.

### 2.1 Core Map Component (`WateenMap.tsx`)

- [ ] Create `src/components/maps/WateenMap.tsx`.
- [ ] Implementation Details:
  - Render `MapContainer` with `center={[30.0444, 31.2357]}` (Cairo) and `zoom={13}`.
  - Add `TileLayer`:
    - Url: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
    - Attribution: `&copy; OpenStreetMap contributors`
  - **Critical:** Include logic to fix default icons inside a `useEffect`:

    ```typescript
    import L from "leaflet";
    import "leaflet/dist/leaflet.css";

    // Fix icons
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "/leaflet/marker-icon-2x.png", // Review if we need to copy assets or perform other fixes
      iconUrl: "/leaflet/marker-icon.png",
      shadowUrl: "/leaflet/marker-shadow.png",
    });
    // NOTE: Alternatively, import images directly or use base64 if asset copying is not preferred.
    // For this task, use standard Leaflet asset imports if valid, or a known fix pattern.
    ```

  - Accept `className` prop to allow height overrides (default to `h-[400px] w-full`).

### 2.2 Client-Side Wrapper (`MapCaller.tsx`)

- [ ] Create `src/components/maps/MapCaller.tsx`.
- [ ] Use `next/dynamic` to import `WateenMap`:

  ```typescript
  import dynamic from 'next/dynamic';

  const WateenMap = dynamic(() => import('./WateenMap'), {
    ssr: false,
    loading: () => <div className="h-[400px] w-full bg-gray-100 animate-pulse flex items-center justify-center">Loading Map...</div>
  });

  export default WateenMap;
  ```

### 2.3 Interactive Features

#### Location Picker (`LocationPicker.tsx`)

- [ ] Create `src/components/maps/LocationPicker.tsx`.
- [ ] Use `useMapEvents` hook to detect clicks:
  ```typescript
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng);
    },
  });
  ```
- [ ] Render a draggable `Marker` at the selected position.

#### Live Tracker (`LiveTracker.tsx`)

- [ ] Create `src/components/maps/LiveTracker.tsx`.
- [ ] Accept `nurseLocation` prop `{ lat: number, lng: number }`.
- [ ] Render a `Marker` that updates reference/position when props change.
- [ ] Consider using a distinct icon color or SVG for the nurse.

## 3. Verification Page

- [ ] Create `src/app/test/map/page.tsx`.
- [ ] Implementation:
  - Import `MapCaller` (the dynamic wrapper).
  - Use `LocationPicker` inside the map context (pass as children or composed component).
  - Display selected coordinates on screen and log to console.
- [ ] Check console for hydration errors (should be none due to `ssr: false`).
- [ ] Verify map tiles load and interaction works.
        