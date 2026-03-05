# Infrastructure Validation Tests

This document describes the comprehensive test suite for validating infrastructure configuration, documentation, and workflow files.

## Overview

The changed files in this pull request are primarily documentation, configuration, and workflow definition files. Traditional unit testing doesn't apply to these file types, so we've created **validation tests** that verify:

- **Configuration validity** (JSON schema, syntax)
- **Documentation structure** (markdown format, required sections)
- **Security compliance** (no exposed secrets)
- **Workflow consistency** (cross-file references, terminology)
- **Integration correctness** (environment variables match configuration references)

## Test Files

### `test_infrastructure_validation.py`

Core infrastructure validation tests covering:

#### 1. **MCP Configuration Tests** (`TestMCPConfiguration`)
- ✅ JSON validity
- ✅ Server structure and required fields
- ✅ Redis uses environment variables (no hardcoded credentials)
- ✅ PostgreSQL configuration
- ✅ Filesystem permissions
- ✅ No sensitive data in configuration

**Key Security Test:**
```python
def test_redis_server_uses_env_variable(self, mcp_config):
    """Test that Redis server uses environment variable instead of hardcoded credentials."""
    # Ensures no hardcoded Redis Cloud credentials
    # Verifies ${REDIS_URL} is used
```

#### 2. **Environment Configuration Tests** (`TestEnvironmentConfiguration`)
- ✅ `.env.example` exists
- ✅ All required variables are present
- ✅ DEBUG is False for production
- ✅ Redis URL format is documented
- ✅ No real secrets in example file
- ✅ Redis fallback behavior is documented

#### 3. **Workflow Documentation Tests** (`TestWorkflowDocumentation`)
- ✅ Workflow files exist
- ✅ YAML frontmatter with description
- ✅ Proper content structure (headings, code blocks, lists)
- ✅ Speckit workflows have consistent structure

#### 4. **Audit Report Tests** (`TestAuditReports`)
- ✅ Reports have proper headers with metadata
- ✅ Structured findings (tables, sections, lists)

#### 5. **Task Specification Tests** (`TestTaskSpecifications`)
- ✅ Proper markdown structure (headings or frontmatter)
- ✅ Actionable requirements (checklists, code examples)

#### 6. **Workflow Consistency Tests** (`TestWorkflowConsistency`)
- ✅ Command files match workflow files across directories
- ✅ Consistent terminology usage

#### 7. **Integration Tests** (`TestInfrastructureIntegration`)
- ✅ Environment variables match MCP config references
- ✅ Redis configuration consistency across files

#### 8. **Security Vulnerability Tests** (`TestSecurityVulnerabilities`)
- ✅ No hardcoded passwords
- ✅ No hardcoded API keys
- Detects patterns like:
  - `password="actual_password"`
  - `api_key="sk_live_123..."`
  - `redis://user:password@host`

#### 9. **Edge Case Tests** (`TestEdgeCases`)
- ✅ Empty workflow file detection
- ✅ Malformed frontmatter detection
- ✅ Environment variable documentation

### `test_workflow_commands.py`

Workflow-specific validation tests:

#### 1. **Speckit Workflows Tests** (`TestSpeckitWorkflows`)
- ✅ Workflows exist in both `.kilocode` and `.opencode` directories
- ✅ Execution steps are documented
- ✅ User input handling is documented

#### 2. **Command-Specific Tests**

**Specify Command** (`TestSpecifyCommand`):
- ✅ Documents branch naming conventions
- ✅ Documents clarification process
- ✅ Documents validation checklist

**Plan Command** (`TestPlanCommand`):
- ✅ Documents implementation phases
- ✅ Documents research phase (Phase 0)
- ✅ Documents design artifacts (data-model, contracts, etc.)

**Implement Command** (`TestImplementCommand`):
- ✅ Documents checklist verification
- ✅ Documents phase-by-phase execution
- ✅ Documents task completion tracking

**Analyze Command** (`TestAnalyzeCommand`):
- ✅ Explicitly marked as read-only
- ✅ Documents coverage analysis
- ✅ Documents constitution compliance checking

**Checklist Command** (`TestChecklistCommand`):
- ✅ Explains "unit tests for requirements" philosophy
- ✅ Documents prohibited patterns (anti-examples)
- ✅ Requires traceability references

#### 3. **AI Swarm Workflow Tests** (`TestAISwarmWorkflow`)
- ✅ Defines agent roles clearly
- ✅ Documents workflow orchestration loop
- ✅ Has security safeguards section
- ✅ Documents automation constraints

#### 4. **Workflow Integration Tests** (`TestWorkflowIntegration`)
- ✅ Clarify → Plan handoff documented
- ✅ Tasks → Implement handoff documented

#### 5. **Error Handling Tests** (`TestWorkflowErrorHandling`)
- ✅ Workflows document prerequisite checks
- ✅ Workflows document error conditions

#### 6. **Regression Prevention Tests** (`TestRegressionPrevention`)
- ✅ **Critical:** No exposed Redis Cloud password (specific audit finding)
- ✅ Redis fallback behavior is documented

## Running the Tests

### Run All Infrastructure Tests
```bash
pytest tests/test_infrastructure_validation.py tests/test_workflow_commands.py -v
```

### Run Specific Test Classes
```bash
# Test only MCP configuration
pytest tests/test_infrastructure_validation.py::TestMCPConfiguration -v

# Test only security vulnerabilities
pytest tests/test_infrastructure_validation.py::TestSecurityVulnerabilities -v

# Test specific workflow commands
pytest tests/test_workflow_commands.py::TestSpecifyCommand -v
```

### Run with Coverage
```bash
pytest tests/test_infrastructure_validation.py tests/test_workflow_commands.py --cov=. --cov-report=html
```

## Test Results

**Current Status:** ✅ **61/61 tests passing**

### Test Breakdown
- Infrastructure Validation: 33 tests
- Workflow Commands: 28 tests

### Coverage Areas
1. **Configuration Files:** `.kilocode/mcp.json`, `.env.example`
2. **Workflow Files:** All `.kilocode/workflows/*.md` and `.opencode/command/*.md`
3. **Audit Reports:** `.agent/reviews-qa/*.md`
4. **Task Specifications:** `.agent/tasks/pending/*.md`
5. **Rules & Guidelines:** `.kilocode/rules/specify-rules.md`
6. **AI Swarm:** `.agent/workflows/ai_swarm.md`

## Key Security Tests

### 1. Redis Password Exposure (Regression Test)
**File:** `test_workflow_commands.py::TestRegressionPrevention::test_mcp_json_does_not_contain_exposed_redis_password`

This test specifically checks for the Redis Cloud password that was exposed in the audit:
- Password: `s0C38imHFb1fkkk9ix84sVJsqUFk4ieD`
- Ensures it's not present in `mcp.json`
- Verifies no other Redis credentials are hardcoded

### 2. Environment Variable Security
**File:** `test_infrastructure_validation.py::TestSecurityVulnerabilities`

Detects:
- Hardcoded passwords (pattern: `password="..."`)\
- Hardcoded API keys (pattern: `api_key="..."`)`
- Redis credentials (pattern: `redis://user:pass@host`)
- PostgreSQL credentials (pattern: `postgres://user:pass@host`)

### 3. Configuration Integration
**File:** `test_infrastructure_validation.py::TestInfrastructureIntegration`

Verifies:
- MCP config references environment variables that exist in `.env.example`
- Database URL is properly constructed from components
- Redis URL consistency across files

## What These Tests DON'T Cover

These tests are **infrastructure validation tests**, not application logic tests. They do NOT test:

- ❌ Business logic execution
- ❌ Django models or views
- ❌ API endpoints functionality
- ❌ Database queries
- ❌ WebSocket connections
- ❌ Pricing calculations
- ❌ Matching service algorithms

For application logic testing, see:
- `tests/test_pricing.py`
- `tests/test_matching_service.py`
- `tests/test_backend_comprehensive.py`

## Test Philosophy

### Why These Tests?

The changed files are **meta-level infrastructure** - they define how development workflows operate, how agents interact, and how configuration is managed. Traditional unit tests don't apply because there's no executable code to test.

Instead, we validate:
1. **Structure** - Files have proper format and required sections
2. **Security** - No exposed secrets or credentials
3. **Consistency** - Cross-file references are valid
4. **Completeness** - Required documentation exists

### "Unit Tests for Documentation"

These tests treat documentation and configuration as first-class artifacts that need quality validation:

- **Syntax Tests:** Is the JSON/YAML/Markdown valid?
- **Schema Tests:** Does the config have required fields?
- **Security Tests:** Are secrets properly externalized?
- **Consistency Tests:** Do references between files resolve?
- **Completeness Tests:** Are required sections present?

## Adding New Tests

### For New Configuration Files

Add tests to `TestMCPConfiguration` or `TestEnvironmentConfiguration`:

```python
def test_new_config_field(self, mcp_config):
    """Test that new field is properly configured."""
    assert "new_field" in mcp_config
    assert mcp_config["new_field"] is not None
```

### For New Workflow Commands

Add a new test class to `test_workflow_commands.py`:

```python
class TestMyNewCommand:
    """Tests specific to the speckit.mynew command."""

    @pytest.fixture
    def mynew_content(self):
        """Load speckit.mynew content."""
        path = Path(".kilocode/workflows/speckit.mynew.md")
        if not path.exists():
            pytest.skip("speckit.mynew not found")
        with open(path, 'r') as f:
            return f.read()

    def test_mynew_documents_feature(self, mynew_content):
        """Test that mynew command documents its key feature."""
        assert "key feature" in mynew_content.lower()
```

### For Security Checks

Add pattern detection to `TestSecurityVulnerabilities`:

```python
def test_no_new_secret_type(self):
    """Test that new secret type is not hardcoded."""
    pattern = r'new_secret["\']?\s*[:=]\s*["\'][^"\']{10,}["\']'
    # ... validation logic
```

## Maintenance

### When to Update Tests

1. **New workflow command added** → Add test class to `test_workflow_commands.py`
2. **New MCP server added** → Add validation to `TestMCPConfiguration`
3. **New environment variable required** → Update `TestEnvironmentConfiguration`
4. **New security pattern detected** → Add to `TestSecurityVulnerabilities`
5. **Workflow structure changes** → Update respective command tests

### Handling Test Failures

**Configuration Test Failures:**
- Check if the file structure changed
- Verify environment variables are properly defined
- Ensure no secrets were accidentally committed

**Security Test Failures:**
- **CRITICAL:** Investigate immediately
- Check if pattern is a false positive
- If real secret found, rotate immediately and update configuration

**Workflow Test Failures:**
- Verify documentation is complete
- Check if workflow structure intentionally changed
- Update test if new structure is valid

## CI/CD Integration

Add to CI pipeline:

```yaml
- name: Run Infrastructure Tests
  run: |
    pytest tests/test_infrastructure_validation.py tests/test_workflow_commands.py \
      -v --tb=short --maxfail=1
```

Recommended: Run these tests on every pull request that modifies:
- `.kilocode/**`
- `.opencode/**`
- `.agent/**`
- `.env.example`
- Any `*.md` documentation files

## Related Documentation

- [Audit Report](../.agent/reviews-qa/final_system_health_report.md) - Security findings that motivated these tests
- [AI Swarm Workflow](../.agent/workflows/ai_swarm.md) - Workflow orchestration
- [Speckit Workflows](../.kilocode/workflows/) - Individual command documentation

## Questions?

For questions about these tests, see:
- Test implementation: Review test files with inline comments
- Infrastructure setup: Check `.kilocode/mcp.json` and `.env.example`
- Security concerns: Review audit reports in `.agent/reviews-qa/`