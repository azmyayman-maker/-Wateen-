# Phase 3 - Ticket 3.2 (Enhanced): Functional Geospatial System (Map Implementation)

**Context:**
We are executing **Phase 3, Ticket 3.2 (Enhanced)** of the Wateen Master Implementation Plan. This task focuses on building the **Functional Geospatial System** using React-Leaflet, Zustand, and OpenStreetMap (Nominatim). This is NOT just a UI task; it involves global state management and address resolution logic.

**Tech Stack:** Next.js 14 (App Router), Tailwind CSS, TypeScript, Lucide React, Zustand, React-Leaflet.

## Critical Architectural Decisions

1.  **Global State:** Use **Zustand** to manage the selected location `{ lat, lng, address, zoom }`. This allows the Booking Form to read the location without prop drilling.
2.  **Reverse Geocoding:** Implement a utility to fetch readable addresses from OpenStreetMap (Nominatim API) when the pin moves.
3.  **Custom Icons:** Do NOT use default Leaflet images (they break in Next.js). Use `L.divIcon` combined with **Lucide React** icons rendered as HTML strings (using `ReactDOMServer` or similar).
4.  **SSR Handling:** Leaflet components must be dynamically imported with `{ ssr: false }`.

---

## Detailed Implementation Steps

### Step 1: Dependencies

- [ ] Install required packages:
  ```bash
  npm install leaflet react-leaflet zustand
  npm install -D @types/leaflet
  ```

### Step 2: Global Location Store (`src/store/useLocationStore.ts`)

- [ ] Create a Zustand store to manage map state.
  - **State:**
    - `latitude`: number | null
    - `longitude`: number | null
    - `address`: string | null
    - `isLoadingAddress`: boolean
  - **Actions:**
    - `setLocation(lat: number, lng: number)`
    - `setAddress(address: string)`
  - **Thunk/Logic:**
    - Implement `fetchAddress(lat, lng)`:
      - Call `https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}`.
      - Update `address` in the store on success.
      - Handle loading state (`isLoadingAddress`).
    - **Note:** Add simple debounce logic to avoid hitting the API on every drag pixel.

### Step 3: Map Utilities (`src/lib/mapUtils.ts`)

- [ ] Create helper functions for custom icons using `L.divIcon` and Lucide icons.
  - `createNurseIcon()`: Returns an `L.DivIcon` containing a Lucide `Stethoscope` or `UserCheck` icon.
  - `createPatientIcon()`: Returns an `L.DivIcon` containing a Lucide `MapPin` icon (Red color).
  - **Styling:** Use Tailwind classes inside the `className` of `L.divIcon` (e.g., `w-8 h-8 text-red-600`).
  - **Implementation Tip:** Convert the Lucide React component to an HTML string (e.g., using `renderToString`) to embed it within the `L.divIcon` html property.

### Step 4: Map Components (`src/components/maps/`)

- [ ] **1. `MapCaller.tsx`**:
  - Create a client-side wrapper for the map.
  - Use `next/dynamic` to import `WateenMap` with `{ ssr: false }`.
  - This ensures Leaflet only runs on the client.

- [ ] **2. `WateenMap.tsx`**:
  - The core map component.
  - **Props:** `mode` ('picker' | 'tracker' | 'static').
  - **Render:** `<MapContainer>` with `<TileLayer>` (OSM).
  - **Default Center:** Cairo `[30.0444, 31.2357]`.
  - Include `LocationPicker` (if mode is 'picker').

- [ ] **3. `LocationPicker.tsx`**:
  - Use `useMapEvents` hook to handle interactions.
  - **Events:** Detect clicks and drags.
  - **On Drag End / Click:** Update `useLocationStore` with new coordinates and trigger `fetchAddress`.
  - **Visual:** Display the "Patient Icon" at the center or clicked point.

- [ ] **4. `AddressDisplay.tsx`**:
  - A small UI overlay on the map (top-right or bottom-left).
  - Connect to `useLocationStore`.
  - **Render:**
    - Display the current `address`.
    - Show a spinner or "Loading..." text if `isLoadingAddress` is true.
    - Application of Tailwind styles for a polished look.

### Step 5: Verification Page (`src/app/test/map/page.tsx`)

- [ ] Create a page that renders `<MapCaller mode="picker" />`.
- [ ] Below the map, display debug info from the store to confirm Zustand integration:
  - "Selected Coordinates: {lat}, {lng}"
  - "Address: {address}"

---

**Action:**
Once this task file is created, trigger the OpenCode agent to execute these steps sequentially.
