# Tasks: Redis Cloud Integration

**Input**: Design documents from `/specs/003-redis-cloud-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included for this feature as it involves critical infrastructure changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `config/`, `docker/`, `visits/`, `tests/` at repository root
- Paths are relative to project root `d:/projects/Wateen/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and dependency verification

- [x] T001 Verify redis, django-redis, and channels-redis are in requirements/base.txt
- [x] T002 [P] Add REDIS_URL to .env.example with format documentation
- [x] T003 [P] Create visits/management/commands/ directory structure if not exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration changes that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Update CACHES configuration in config/settings.py to use REDIS_URL environment variable
- [x] T005 Update CHANNEL_LAYERS configuration in config/settings.py to use REDIS_URL environment variable
- [x] T006 Add connection pool configuration (max_connections: 50) to CACHES in config/settings.py
- [x] T007 [P] Remove redis service from docker/docker-compose.yml
- [x] T008 [P] Remove redis_data volume from docker/docker-compose.yml
- [x] T009 Update web service depends_on in docker/docker-compose.yml to remove redis dependency
- [x] T010 Add REDIS_URL to web service environment in docker/docker-compose.yml

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Redis Cloud Connection (Priority: P1) 🎯 MVP

**Goal**: Django application connects to Redis Cloud instead of local Redis instance

**Independent Test**: Run `python manage.py test_redis` command and verify "Redis Connected Successfully" output

### Tests for User Story 1

- [x] T011 [P] [US1] Create test file tests/test_redis_cloud.py with connection test cases
- [x] T012 [P] [US1] Add test for successful Redis Cloud connection in tests/test_redis_cloud.py
- [x] T013 [P] [US1] Add test for connection failure handling in tests/test_redis_cloud.py

### Implementation for User Story 1

- [x] T014 [US1] Create test_redis management command in visits/management/commands/test_redis.py
- [x] T015 [US1] Implement cache connection test in test_redis command
- [x] T016 [US1] Implement channel layer connection test in test_redis command
- [x] T017 [US1] Add success output "Redis Connected Successfully" to test_redis command
- [x] T018 [US1] Add error handling and descriptive error messages to test_redis command

**Checkpoint**: At this point, User Story 1 should be fully functional - can verify Redis Cloud connectivity

---

## Phase 4: User Story 2 - Cache Operations (Priority: P2)

**Goal**: Django cache backend uses Redis Cloud for caching with connection pooling

**Independent Test**: Store and retrieve cached values through Django's cache API

### Tests for User Story 2

- [x] T019 [P] [US2] Add cache set/get test in tests/test_redis_cloud.py
- [x] T020 [P] [US2] Add cache expiration test in tests/test_redis_cloud.py
- [x] T021 [P] [US2] Add connection pool limit test in tests/test_redis_cloud.py

### Implementation for User Story 2

- [x] T022 [US2] Verify cache operations work with Redis Cloud URL in config/settings.py
- [x] T023 [US2] Add socket_timeout and socket_connect_timeout to cache OPTIONS in config/settings.py
- [x] T024 [US2] Add retry_on_timeout to connection pool OPTIONS in config/settings.py

**Checkpoint**: At this point, cache operations should work correctly with Redis Cloud

---

## Phase 5: User Story 3 - WebSocket Channel Layers (Priority: P3)

**Goal**: Django Channels uses Redis Cloud for channel layers across multiple instances

**Independent Test**: Send message through WebSocket and verify receipt by intended recipient

### Tests for User Story 3

- [ ] T025 [P] [US3] Add channel layer send/receive test in tests/test_redis_cloud.py
- [ ] T026 [P] [US3] Add channel group test in tests/test_redis_cloud.py

### Implementation for User Story 3

- [ ] T027 [US3] Verify channel layer configuration uses REDIS_URL in config/settings.py
- [ ] T028 [US3] Test WebSocket connection through existing visits consumers

**Checkpoint**: At this point, WebSocket communication should work through Redis Cloud

---

## Phase 6: User Story 4 - Docker Environment Configuration (Priority: P4)

**Goal**: Docker environment passes Redis Cloud credentials without local Redis container

**Independent Test**: Start Docker environment and verify application connects to Redis Cloud

### Tests for User Story 4

- [ ] T029 [P] [US4] Add Docker integration test in tests/test_redis_cloud.py
- [ ] T030 [P] [US4] Add test for REDIS_URL environment variable availability in tests/test_redis_cloud.py

### Implementation for User Story 4

- [ ] T031 [US4] Verify docker-compose.yml has no local Redis service
- [ ] T032 [US4] Verify web service has REDIS_URL in environment variables
- [ ] T033 [US4] Test full Docker stack startup with `docker compose up`

**Checkpoint**: At this point, Docker environment should work correctly with Redis Cloud

---

## Phase 7: Graceful Degradation (Cross-Cutting)

**Purpose**: Implement fallback behavior when Redis Cloud is unavailable

- [ ] T034 [P] Create cache fallback decorator in visits/services/cache_fallback.py
- [ ] T035 Implement database fallback for cache misses in cache_fallback.py
- [ ] T036 [P] Add logging for Redis unavailability events in config/settings.py
- [ ] T037 Add WebSocket feature disabled notification in visits/consumers.py
- [ ] T038 [P] Add test for graceful degradation in tests/test_redis_cloud.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final verification

- [x] T039 [P] Update README.md with Redis Cloud configuration instructions
- [x] T040 [P] Run all tests with `pytest tests/test_redis_cloud.py -v`
- [x] T041 Run quickstart.md validation - verify all steps work
- [x] T042 [P] Code cleanup and remove any hardcoded Redis references
- [x] T043 Final verification: run `python manage.py test_redis` and confirm success

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2 → P3 → P4)
- **Graceful Degradation (Phase 7)**: Can run after Phase 2, parallel with user stories
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of other stories

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- Graceful Degradation tasks marked [P] can run in parallel with user stories

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create test file tests/test_redis_cloud.py with connection test cases"
Task: "Add test for successful Redis Cloud connection in tests/test_redis_cloud.py"
Task: "Add test for connection failure handling in tests/test_redis_cloud.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `python manage.py test_redis`
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test cache operations → Deploy/Demo
4. Add User Story 3 → Test WebSocket → Deploy/Demo
5. Add User Story 4 → Test Docker → Deploy/Demo
6. Add Graceful Degradation → Full feature complete

---

## Summary

| Phase                         | Tasks  | Parallel Tasks |
| ----------------------------- | ------ | -------------- |
| Phase 1: Setup                | 3      | 2              |
| Phase 2: Foundational         | 7      | 2              |
| Phase 3: User Story 1         | 8      | 3              |
| Phase 4: User Story 2         | 6      | 3              |
| Phase 5: User Story 3         | 4      | 2              |
| Phase 6: User Story 4         | 5      | 2              |
| Phase 7: Graceful Degradation | 5      | 3              |
| Phase 8: Polish               | 5      | 3              |
| **Total**                     | **43** | **20**         |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
