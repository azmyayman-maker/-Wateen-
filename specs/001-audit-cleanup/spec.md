# Feature Specification: Post-Audit Codebase Cleanup & Fixes

**Feature Branch**: `001-audit-cleanup`  
**Created**: 2026-02-19  
**Status**: Draft  
**Input**: User description: "Resolve all 8 identified issues across script files, docker configuration, and tests to ensure a clean, warning-free, and secure codebase."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Code Quality Validation (Priority: P1)

As a developer, I need the codebase to pass linting checks without warnings so that code quality standards are maintained and potential issues are caught early.

**Why this priority**: Clean code without linting warnings is foundational to maintainability and prevents technical debt accumulation.

**Independent Test**: Run `flake8 .` command and verify zero warnings/errors are reported.

**Acceptance Scenarios**:

1. **Given** the scripts directory contains Python files, **When** flake8 is run, **Then** no unused import warnings are reported
2. **Given** socket connection code exists, **When** flake8 is run, **Then** no resource cleanup warnings are reported
3. **Given** f-strings are used in print statements, **When** flake8 is run, **Then** no unnecessary f-string warnings are reported

---

### User Story 2 - Secure Configuration (Priority: P1)

As a DevOps engineer, I need configuration files to use environment variables instead of hardcoded secrets so that sensitive credentials are not exposed in the codebase.

**Why this priority**: Security is critical - hardcoded secrets in version control represent a significant security risk.

**Independent Test**: Inspect docker-compose.yml and verify no literal database URLs or passwords are present; verify services bind to localhost only.

**Acceptance Scenarios**:

1. **Given** the docker-compose.yml file, **When** reviewed, **Then** DATABASE_URL uses environment variable substitution
2. **Given** the docker-compose.yml file, **When** reviewed, **Then** REDIS_URL uses environment variable substitution
3. **Given** exposed ports in docker-compose.yml, **When** reviewed, **Then** all ports bind to 127.0.0.1 (localhost only)

---

### User Story 3 - Resource Management (Priority: P2)

As a developer, I need network resources to be properly cleaned up so that connections are not leaked and system resources are freed appropriately.

**Why this priority**: Proper resource cleanup prevents memory leaks and connection pool exhaustion.

**Independent Test**: Run verification scripts and ensure pubsub connections are properly closed; verify socket connections use context managers.

**Acceptance Scenarios**:

1. **Given** Redis pubsub operations, **When** operations complete (success or failure), **Then** unsubscribe and close are always called
2. **Given** socket connection code, **When** connection is established, **Then** context manager ensures automatic cleanup

---

### User Story 4 - Test Suite Integrity (Priority: P2)

As a developer, I need the test suite to pass reliably so that CI/CD pipelines function correctly and code changes can be validated.

**Why this priority**: Reliable tests are essential for maintaining code quality and enabling safe refactoring.

**Independent Test**: Run `pytest visits/tests/test_edge_cases.py` and verify all tests pass or are appropriately skipped.

**Acceptance Scenarios**:

1. **Given** the test_edge_cases.py test file, **When** tests run, **Then** no mock-related failures occur
2. **Given** placeholder tests exist, **When** tests run, **Then** they are properly skipped with clear reasons
3. **Given** get_factor mocking, **When** test_money_precision runs, **Then** correct Decimal values are returned

---

### User Story 5 - Proper Logging (Priority: P3)

As a developer, I need exceptions to be logged appropriately so that issues can be diagnosed when they occur in production.

**Why this priority**: While important, this is less critical than security or test failures.

**Independent Test**: Trigger exception conditions in pricing service and verify warning logs are generated.

**Acceptance Scenarios**:

1. **Given** pricing factor lookup fails, **When** exception occurs, **Then** warning is logged with factor key and error details
2. **Given** the pricing service, **When** night hours check is needed externally, **Then** public method is available

---

### Edge Cases

- What happens when password-only URLs (no username) need to be masked? The masking function must handle `redis://:pass@host` format correctly
- What happens when socket connection fails? Context manager should still properly clean up any allocated resources
- What happens when pubsub operations fail mid-stream? Finally block ensures cleanup still occurs

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Scripts MUST NOT contain unused imports (urllib.parse, os)
- **FR-002**: Resource-intensive operations (pubsub, sockets) MUST use proper cleanup patterns (try/finally or context managers)
- **FR-003**: URL password masking MUST handle edge cases including password-only URLs
- **FR-004**: Configuration files MUST NOT contain hardcoded secrets or credentials
- **FR-005**: Service ports MUST bind to localhost (127.0.0.1) only to prevent external network access
- **FR-006**: Exception handlers MUST log warnings instead of silently passing
- **FR-007**: Pricing service MUST expose public method for night hours checking
- **FR-008**: Test mocks MUST align with actual method signatures
- **FR-009**: Placeholder tests MUST use proper skip decorators
- **FR-010**: Code formatting MUST follow consistent indentation standards

### Key Entities

- **Script Files**: Python utility scripts that verify connections and audit system state; must be lint-clean
- **Docker Configuration**: Infrastructure configuration files; must use secure practices
- **Pricing Service**: Core business logic for visit pricing; must have proper logging and public API
- **Test Suite**: Automated tests for edge cases; must be reliable and maintainable

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `flake8 .` produces zero warnings or errors
- **SC-002**: Running `pytest visits/tests/test_edge_cases.py` completes with all tests passing or appropriately skipped
- **SC-003**: Running `python scripts/check_conn.py` successfully masks all passwords in URLs including edge cases
- **SC-004**: Docker compose configuration contains zero hardcoded secrets (all credentials use environment variables)
- **SC-005**: All exposed service ports bind exclusively to 127.0.0.1 (no 0.0.0.0 bindings)
- **SC-006**: All exception handlers in pricing service log warnings with contextual information

## Assumptions

- Python 3.11+ environment is in use
- Flake8 is configured with standard rules including ARG001 for unused arguments
- The project follows Django conventions for logging
- Environment variables for DATABASE_URL and REDIS_URL will be provided at deployment time
- The codebase uses pytest for testing with unittest.skip available

## Dependencies

- Existing scripts in the scripts/ directory
- Docker compose configuration in docker/ directory
- Pricing service implementation in visits/services/pricing.py
- Test suite in visits/tests/test_edge_cases.py
- Pytest configuration in testsprite_tests/conftest.py
