# Tasks: Frontend Initialization

**Input**: Design documents from `/specs/004-frontend-init/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Not explicitly requested - tests excluded from this task list.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for source code
- Paths assume Next.js 14 App Router structure

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Next.js 14 project with TypeScript and Tailwind CSS

- [ ] T001 Initialize Next.js 14 project with TypeScript, Tailwind, ESLint in `frontend/`
- [ ] T002 [P] Install Cairo font dependency via `next/font/google` in `frontend/package.json`
- [ ] T003 [P] Configure TypeScript strict mode in `frontend/tsconfig.json`
- [ ] T004 [P] Create project directory structure per plan.md in `frontend/src/`

---

## Phase 2: Foundational (Core Design System)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Configure Tailwind CSS with custom theme (colors, fonts, RTL) in `frontend/tailwind.config.ts`
- [ ] T006 [P] Create CSS custom properties for design tokens in `frontend/src/app/globals.css`
- [ ] T007 [P] Create utility functions (cn helper) in `frontend/src/lib/utils.ts`
- [ ] T008 [P] Create shared Button component with variants in `frontend/src/components/shared/Button.tsx`
- [ ] T009 [P] Create shared Input component with accessibility in `frontend/src/components/shared/Input.tsx`
- [ ] T010 [P] Create shared Card component in `frontend/src/components/shared/Card.tsx`
- [ ] T011 Create component barrel export in `frontend/src/components/shared/index.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - RTL Arabic Homepage Display (Priority: P1) 🎯 MVP

**Goal**: Display homepage with proper RTL Arabic layout, Cairo font, and welcome message

**Independent Test**: Load homepage, verify RTL direction, Cairo font, and centered Arabic welcome message

### Implementation for User Story 1

- [ ] T012 [US1] Configure root layout with Cairo font, RTL, and Arabic lang in `frontend/src/app/layout.tsx`
- [ ] T013 [US1] Create homepage with centered Arabic welcome message in `frontend/src/app/page.tsx`
- [ ] T014 [US1] Add skip-to-content link for accessibility in `frontend/src/app/layout.tsx`
- [ ] T015 [US1] Verify contrast ratios meet WCAG 2.1 AA (Cyan-600 on white = 4.58:1)
- [ ] T016 [US1] Run production build to verify zero errors: `npm run build`

**Checkpoint**: Homepage displays RTL Arabic correctly - MVP complete

---

## Phase 4: User Story 2 - Authentication Pages Structure (Priority: P2)

**Goal**: Create login and registration pages with RTL layout

**Independent Test**: Navigate to `/login` and `/register`, verify pages render with RTL and Cairo font

### Implementation for User Story 2

- [ ] T017 [P] [US2] Create auth route group layout in `frontend/src/app/(auth)/layout.tsx`
- [ ] T018 [P] [US2] Create login page with placeholder form in `frontend/src/app/(auth)/login/page.tsx`
- [ ] T019 [P] [US2] Create register page with placeholder form in `frontend/src/app/(auth)/register/page.tsx`
- [ ] T020 [US2] Add proper heading hierarchy (h1 → h2) to auth pages
- [ ] T021 [US2] Verify all form inputs have associated labels (accessibility)

**Checkpoint**: Auth pages render with RTL - User Story 2 complete

---

## Phase 5: User Story 3 - Dashboard Route Structure (Priority: P3)

**Goal**: Create patient and nurse dashboard routes with RTL layout

**Independent Test**: Navigate to `/patient` and `/nurse`, verify pages render with RTL and Cairo font

### Implementation for User Story 3

- [ ] T022 [P] [US3] Create dashboard route group layout in `frontend/src/app/(dashboard)/layout.tsx`
- [ ] T023 [P] [US3] Create patient dashboard page in `frontend/src/app/(dashboard)/patient/page.tsx`
- [ ] T024 [P] [US3] Create nurse dashboard page in `frontend/src/app/(dashboard)/nurse/page.tsx`
- [ ] T025 [US3] Add placeholder content structure to dashboard pages

**Checkpoint**: Dashboard routes render with RTL - User Story 3 complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and optimization

- [ ] T026 [P] Create 404 not-found page in `frontend/src/app/not-found.tsx`
- [ ] T027 [P] Add Arabic fallback font stack (Amiri, Noto Sans Arabic) to Tailwind config
- [ ] T028 Run Lighthouse accessibility audit on all routes
- [ ] T029 Verify Core Web Vitals meet "Good" thresholds (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] T030 Run final production build and verify all 5 routes render correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable

### Within Each User Story

- Root layout before pages (US1)
- Layouts before page content (US2, US3)
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004 can run in parallel (Phase 1)
- T006, T007, T008, T009, T010 can run in parallel (Phase 2)
- T017, T018, T019 can run in parallel (Phase 4)
- T022, T023, T024 can run in parallel (Phase 5)
- T026, T027 can run in parallel (Phase 6)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all foundational components together:
Task: "Create CSS custom properties in frontend/src/app/globals.css"
Task: "Create utility functions in frontend/src/lib/utils.ts"
Task: "Create shared Button component in frontend/src/components/shared/Button.tsx"
Task: "Create shared Input component in frontend/src/components/shared/Input.tsx"
Task: "Create shared Card component in frontend/src/components/shared/Card.tsx"
```

---

## Parallel Example: User Story 2 (Auth Pages)

```bash
# Launch all auth page tasks together:
Task: "Create auth route group layout in frontend/src/app/(auth)/layout.tsx"
Task: "Create login page in frontend/src/app/(auth)/login/page.tsx"
Task: "Create register page in frontend/src/app/(auth)/register/page.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test homepage independently
5. Deploy/demo if ready - Arabic RTL homepage is live

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Complete Polish → Final optimization

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Homepage)
   - Developer B: User Story 2 (Auth Pages)
   - Developer C: User Story 3 (Dashboards)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Cairo font optimization via `next/font/google` is critical for performance
- All colors must meet WCAG 2.1 AA contrast requirements
