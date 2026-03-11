# 🤖 Wateen B2B2C — Multi-Agent System Protocol & Core Rules

> **Version:** 3.0 | **Updated:** March 2026 | **Status:** ACTIVE
> **Execution Model:** Multi-Agent Orchestration via Speckit Workflow

---

## 1. CRITICAL CONTEXT — THE B2B2C AGGREGATOR
Wateen is a **B2B2C Healthcare Aggregator** — NOT a P2P marketplace.
We connect Patients with MoH-Licensed Nursing Agencies.
- **NEVER** treat nurses as independent freelancers.
- **NEVER** bypass the Agency layer in any logic, dispatch, or financial settlement.
- **NurseProfile.agency** is MANDATORY.

## 2. TECHNOLOGY STACK & ARCHITECTURE
- **Backend:** Python 3.11+, Django 5.2, DRF, PostgreSQL 16 + PostGIS 3.4 (All Dockerized)
- **Cache/Real-time:** Redis 7, Celery 5, Django Channels (WebSockets)
- **Frontend:** Next.js 14 (App Router), TypeScript 5, Tailwind CSS, React Admin (B2B Dashboard)
- **Maps (OSM Stack):** react-leaflet, leaflet-geoman, Nominatim, OSRM/ORS
- **Payments:** Stripe Connect (Destination Charges)
- **Language/UX:** Arabic-first (RTL mandatory), `Decimal` strictly for all financial logic.

## 3. CORE DATA MODEL — STRICT ENFORCEMENT
- `CustomUser` (Base) -> Roles: PATIENT, NURSE, ADMIN, AGENCY_ADMIN.
- `AgencyProfile` -> Handles `coverage_polygon` (PostGIS), dispatch mode, wallet, Stripe integration.
- `NurseProfile` -> Linked to Agency (FK). Status: available/offline.
- `Visit` -> Linked to Patient & Agency. Dispatched to Agency first, then assigned to Nurse. Contains immutable `pricing_snapshot`.
  - **State Machine:** `PENDING_AGENCY` → `PENDING_NURSE` → `ACCEPTED` → `EN_ROUTE` → `IN_PROGRESS` → `COMPLETED`.
- `Transaction` -> Platform Fee (15%) + Agency Payout (85%). Status: `PENDING` → `ESCROWED` → `SETTLED`.

---

## 4. THE MULTI-AGENT SYSTEM (MAS) WORKFLOW 🌐

The development of Wateen is driven by a highly professional **Multi-Agent System**. As the Main Agent (Orchestrator), I am responsible for delegating tasks to highly specialized Sub-Agents.

### 4.1 The Speckit Execution Pipeline
Whenever a new **Ticket** or Feature is presented, the Orchestrator MUST strictly follow the Speckit workflow, infusing MAS delegation at the core:

1. **Ticket Initiation:** The user provides the ticket workflow and describes the goals.
2. **`speckit.plan` & `speckit.specify`:** The Orchestrator analyzes the PRD, identifies affected domains, tests architectures using GitNexus, and writes the specifications.
3. **`speckit.tasks` (CRITICAL MAS PHASE):** 
   During the generation of `tasks.md`, the Orchestrator **DOES NOT** just simply list tasks. Instead, it **architects the Multi-Agent System** for this specific ticket.
   - It divides the ticket into hyper-specialized domains (e.g., *PostGIS DB Agent*, *Next.js UI Agent*, *Stripe Escrow Agent*, *Pytest QA Subagent*, *Browser Navigation Subagent*).
   - Each top-level section in `tasks.md` MUST represent a mission assigned to a specific Sub-Agent.
   - The Orchestrator defines the exact prompt, context, constraints, and success criteria for each Sub-Agent so they execute flawlessly.
4. **`speckit.implement`:** The Orchestrator spins up or emulates the Sub-Agents sequentially or concurrently to execute the defined missions. The Orchestrator merges their work, handles GitNexus impact analysis, and ensures zero regressions.

### 4.2 Sub-Agent Emulation / Spawning Rules
When acting as or spawning a Sub-Agent (e.g., via the Browser Subagent tool or via focused contextual emulation):
- **Absolute Focus:** The Sub-Agent only cares about its specific domain (e.g., if it's the UI Agent, it does not touch or hallucinate Django models).
- **Tool Restriction:** Sub-agents must utilize precise tools for their domain (e.g., Pytest for Backend QA, Playwright/Browser Subagent for UI rendering tests).
- **Professional Separation:** Work is handed back to the Orchestrator cleanly as diffs, test logs, or final status reports.

### 4.3 Opencode CLI Integration (Sub-Agent Execution)
**`opencode`** is the officially sanctioned tool for delegating execution tasks to autonomous Sub-Agents via the terminal.
When the Orchestrator reaches the execution phase (`speckit.implement`), it MUST deploy Sub-Agents using the `opencode run` command.

**Execution Rules for Opencode:**
1. **Delegation Prompting:** The Orchestrator will craft a highly restricted and precise prompt for `opencode run "..."`, containing the exact scope of files to edit, the specific task, and the strict boundaries preventing the Sub-Agent from wandering out of scope.
2. **Context Passing:** The Orchestrator must pass relevant context (e.g., "Read `tasks.md` step 2.1 before starting") within the `opencode` command payload.
3. **Observation & Verification:** After a Sub-Agent completes its `opencode run` execution, the Orchestrator ALWAYS assumes the role of QA. The Orchestrator must run the relevant test commands (`pytest`, `npm run lint`, etc.) or check Git diffs to verify the Sub-Agent accurately achieved the goal without breaking the architecture.

## 5. DEVELOPMENT CONSTRAINTS & QUALITY
- **QA is Mandatory:** No ticket is closed without a QA pass by a designated QA Agent. Tests must cover the spatial interactions (`ST_Intersects`) and atomic financial transactions.
- **GitNexus Integration:** Use GitNexus (`.claude/skills/gitnexus/...`) to trace architectural boundaries and blast radius before modifying core logic.
- **No Floating Points:** Use `Decimal` everywhere for money.
- **Arabic-First:** Interfaces must be visually premium, Dark mode supportive, and flawless in RTL alignment.
