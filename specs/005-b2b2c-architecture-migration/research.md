# Phase 0: Research & Clarifications

Based on the technical context extraction from `spec.md`, the following areas required clarification and research.

## 1. Map Provider Decision (Mapbox vs Leaflet)

**Context**: The B2B SaaS Dashboard needs an interactive map widget for drawing the `coverage_polygon` (User Story 2).
**Decision**: **Mapbox GL JS** (via `react-map-gl`).
**Rationale**: Wateen emphasizes a premium, 3D aesthetic (as seen in recent features like the 3D Services Grid). Mapbox provides superior vector rendering, custom styling capabilities for a premium dark mode, and excellent drawing tools (`mapbox-gl-draw`) for geometric polygons. Leaflet, while open-source, lacks the high-end polish out-of-the-box.
**Alternatives considered**: React-Leaflet (rejected due to less premium default rendering), Google Maps JS API (rejected due to complex pricing and less customizable base maps).

## 2. Testing Frameworks

**Context**: The spec mentions rigorous testing (zero data loss, concurrent load testing, escrow accuracy) but doesn't specify the frameworks.
**Decision**:

- Backend: **pytest** with `pytest-django`, plus `locust` for WebSocket/concurrent load testing.
- Frontend: **Jest** + **React Testing Library** for component testing, Cypress/Playwright for E2E flow testing.
  **Rationale**: Pytest is the python ecosystem standard and handles Django DB transactions well. Locust is python-based and excellent for testing WebSocket concurrency (5000 connections).
  **Alternatives considered**: Python's `unittest` (too verbose), JMeter (steeper learning curve than Locust for WS).

## 3. Payment Gateway / Escrow

**Context**: The escrow and financial settlement (User Story 5) requires holding funds and splitting payments (Wateen Take Rate vs Agency Payout).
**Decision**: **Stripe Connect** (Destination or Separate Charges & Transfers).
**Rationale**: Stripe Connect is specifically built for multi-party B2B2C marketplaces. It natively supports Escrow (holding funds on the platform account) and programmable payouts to connected Agency accounts.
**Alternatives considered**: Paymob or local Egyptian gateways (may be required for local compliance, but Stripe provides the best architectural model. If local gateway is enforced by MoH, a custom escrow ledger in the DB is required, which is supported by the proposed `TRANSACTION` entity). _Note: Using the internal `TRANSACTION` entity as the ledger allows flexibility to integrate any gateway later._
