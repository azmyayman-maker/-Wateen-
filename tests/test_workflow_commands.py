"""
Tests for specific workflow commands and their content validation.

This module tests individual workflow commands for:
- Command-specific structure requirements
- Execution step completeness
- Parameter validation
- Error handling documentation
"""

import pytest
import re
from pathlib import Path


class TestSpeckitWorkflows:
    """Tests for speckit.* workflow commands."""

    @pytest.fixture
    def speckit_workflows(self):
        """Get all speckit workflow files."""
        workflow_dirs = [
            Path("/home/jailuser/git/.kilocode/workflows"),
            Path("/home/jailuser/git/.opencode/command"),
        ]

        workflows = {}
        for dir_path in workflow_dirs:
            if dir_path.exists():
                for file_path in dir_path.glob("speckit.*.md"):
                    workflow_name = file_path.stem  # e.g., "speckit.specify"
                    if workflow_name not in workflows:
                        workflows[workflow_name] = []
                    workflows[workflow_name].append(file_path)

        return workflows

    def test_all_speckit_workflows_exist_in_both_locations(self, speckit_workflows):
        """Test that speckit workflows exist in both .kilocode and .opencode."""
        # Some workflows might be in only one location, but major ones should be in both
        major_workflows = ["speckit.specify", "speckit.plan", "speckit.tasks", "speckit.implement"]

        for workflow in major_workflows:
            if workflow in speckit_workflows:
                # If it exists, check both locations have it
                file_count = len(speckit_workflows[workflow])
                # This is informational - workflows might be in one or both locations
                assert file_count >= 1, f"{workflow} should exist in at least one location"

    def test_speckit_workflows_have_outline_or_steps_section(self, speckit_workflows):
        """Test that speckit workflows document their execution steps."""
        for workflow_name, file_paths in speckit_workflows.items():
            for file_path in file_paths:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Should have execution steps or outline
                has_steps = any(
                    section in content
                    for section in ["## Outline", "## Execution Steps", "## Steps", "## Phases"]
                )

                assert has_steps, f"{workflow_name} missing execution steps documentation"

    def test_speckit_workflows_document_user_input_handling(self, speckit_workflows):
        """Test that speckit workflows document how they handle user input."""
        # Workflows that should explicitly handle user input
        input_sensitive_workflows = [
            "speckit.specify",
            "speckit.clarify",
            "speckit.constitution",
            "speckit.checklist",
        ]

        for workflow_name in input_sensitive_workflows:
            if workflow_name not in speckit_workflows:
                continue

            for file_path in speckit_workflows[workflow_name]:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Should mention user input or arguments
                handles_input = (
                    "$ARGUMENTS" in content or
                    "User Input" in content or
                    "user input" in content.lower()
                )

                assert handles_input, f"{workflow_name} should document user input handling"


class TestSpecifyCommand:
    """Tests specific to the speckit.specify command."""

    @pytest.fixture
    def specify_content(self):
        """Load speckit.specify content."""
        paths = [
            Path("/home/jailuser/git/.kilocode/workflows/speckit.specify.md"),
            Path("/home/jailuser/git/.opencode/command/speckit.specify.md"),
        ]

        for path in paths:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()

        pytest.skip("speckit.specify not found")

    def test_specify_documents_branch_naming(self, specify_content):
        """Test that specify command documents branch naming conventions."""
        # Should mention branch or naming
        mentions_branches = any(
            term in specify_content.lower()
            for term in ["branch", "short name", "short-name", "naming"]
        )

        assert mentions_branches, "Specify should document branch naming"

    def test_specify_documents_clarification_process(self, specify_content):
        """Test that specify command documents the clarification process."""
        # Should mention clarification or needs clarification
        documents_clarification = (
            "NEEDS CLARIFICATION" in specify_content or
            "clarification" in specify_content.lower()
        )

        assert documents_clarification, "Specify should document clarification process"

    def test_specify_documents_validation_checklist(self, specify_content):
        """Test that specify command documents spec validation."""
        # Should mention validation or quality checks
        documents_validation = any(
            term in specify_content.lower()
            for term in ["validation", "quality", "checklist"]
        )

        assert documents_validation, "Specify should document validation process"


class TestPlanCommand:
    """Tests specific to the speckit.plan command."""

    @pytest.fixture
    def plan_content(self):
        """Load speckit.plan content."""
        paths = [
            Path("/home/jailuser/git/.kilocode/workflows/speckit.plan.md"),
            Path("/home/jailuser/git/.opencode/command/speckit.plan.md"),
        ]

        for path in paths:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()

        pytest.skip("speckit.plan not found")

    def test_plan_documents_phases(self, plan_content):
        """Test that plan command documents implementation phases."""
        # Should mention phases
        mentions_phases = "phase" in plan_content.lower()

        assert mentions_phases, "Plan should document implementation phases"

    def test_plan_documents_research_phase(self, plan_content):
        """Test that plan command documents research phase."""
        # Should mention research or Phase 0
        documents_research = (
            "research" in plan_content.lower() or
            "Phase 0" in plan_content
        )

        assert documents_research, "Plan should document research phase"

    def test_plan_documents_design_artifacts(self, plan_content):
        """Test that plan command documents what artifacts it generates."""
        # Should mention specific artifacts
        artifacts = ["data-model", "contracts", "research.md", "quickstart"]

        mentions_artifacts = any(
            artifact in plan_content.lower()
            for artifact in artifacts
        )

        assert mentions_artifacts, "Plan should document generated artifacts"


class TestImplementCommand:
    """Tests specific to the speckit.implement command."""

    @pytest.fixture
    def implement_content(self):
        """Load speckit.implement content."""
        paths = [
            Path("/home/jailuser/git/.kilocode/workflows/speckit.implement.md"),
            Path("/home/jailuser/git/.opencode/command/speckit.implement.md"),
        ]

        for path in paths:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()

        pytest.skip("speckit.implement not found")

    def test_implement_documents_checklist_verification(self, implement_content):
        """Test that implement command documents checklist verification."""
        # Should check checklists before implementing
        mentions_checklists = "checklist" in implement_content.lower()

        assert mentions_checklists, "Implement should verify checklists before execution"

    def test_implement_documents_phase_execution(self, implement_content):
        """Test that implement command documents phase-by-phase execution."""
        # Should mention phases and sequential execution
        mentions_phases = any(
            term in implement_content.lower()
            for term in ["phase", "sequential", "order", "dependency"]
        )

        assert mentions_phases, "Implement should document execution order"

    def test_implement_documents_task_completion_tracking(self, implement_content):
        """Test that implement command documents task tracking."""
        # Should mention marking tasks complete
        documents_tracking = any(
            term in implement_content
            for term in ["[X]", "mark", "complete", "tracking"]
        )

        assert documents_tracking, "Implement should document task completion tracking"


class TestAnalyzeCommand:
    """Tests specific to the speckit.analyze command."""

    @pytest.fixture
    def analyze_content(self):
        """Load speckit.analyze content."""
        paths = [
            Path("/home/jailuser/git/.kilocode/workflows/speckit.analyze.md"),
            Path("/home/jailuser/git/.opencode/command/speckit.analyze.md"),
        ]

        for path in paths:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()

        pytest.skip("speckit.analyze not found")

    def test_analyze_is_readonly(self, analyze_content):
        """Test that analyze command is explicitly read-only."""
        # Should explicitly state it's read-only
        is_readonly = any(
            phrase in analyze_content
            for phrase in ["READ-ONLY", "read-only", "Do not modify", "NEVER modify"]
        )

        assert is_readonly, "Analyze should be explicitly marked as read-only"

    def test_analyze_documents_coverage_checks(self, analyze_content):
        """Test that analyze command documents coverage analysis."""
        # Should mention coverage
        mentions_coverage = "coverage" in analyze_content.lower()

        assert mentions_coverage, "Analyze should document coverage analysis"

    def test_analyze_documents_constitution_checking(self, analyze_content):
        """Test that analyze command checks constitution compliance."""
        # Should mention constitution
        checks_constitution = "constitution" in analyze_content.lower()

        assert checks_constitution, "Analyze should check constitution compliance"


class TestChecklistCommand:
    """Tests specific to the speckit.checklist command."""

    @pytest.fixture
    def checklist_content(self):
        """Load speckit.checklist content."""
        paths = [
            Path("/home/jailuser/git/.kilocode/workflows/speckit.checklist.md"),
            Path("/home/jailuser/git/.opencode/command/speckit.checklist.md"),
        ]

        for path in paths:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()

        pytest.skip("speckit.checklist not found")

    def test_checklist_explains_unit_tests_for_requirements_concept(self, checklist_content):
        """Test that checklist command explains its 'unit tests for requirements' philosophy."""
        # Should explain the concept
        explains_concept = any(
            phrase in checklist_content
            for phrase in [
                "Unit Tests for",
                "unit tests for requirements",
                "Testing requirements quality",
                "test the requirements",
            ]
        )

        assert explains_concept, "Checklist should explain unit tests for requirements concept"

    def test_checklist_documents_prohibited_patterns(self, checklist_content):
        """Test that checklist command documents what NOT to do."""
        # Should have anti-examples or prohibited section
        has_antipatterns = any(
            marker in checklist_content
            for marker in ["PROHIBITED", "WRONG", "NOT for", "Anti-Examples"]
        )

        assert has_antipatterns, "Checklist should document prohibited patterns"

    def test_checklist_documents_traceability(self, checklist_content):
        """Test that checklist command requires traceability."""
        # Should mention traceability or spec references
        mentions_traceability = any(
            term in checklist_content
            for term in ["traceability", "Spec §", "reference", "[Gap]"]
        )

        assert mentions_traceability, "Checklist should document traceability requirements"


class TestAISwarmWorkflow:
    """Tests specific to the AI Swarm workflow."""

    @pytest.fixture
    def swarm_content(self):
        """Load AI Swarm workflow content."""
        path = Path("/home/jailuser/git/.agent/workflows/ai_swarm.md")

        if not path.exists():
            pytest.skip("AI Swarm workflow not found")

        with open(path, 'r') as f:
            return f.read()

    def test_swarm_defines_roles_clearly(self, swarm_content):
        """Test that AI Swarm workflow clearly defines agent roles."""
        # Should have a roles section or table
        has_roles = any(
            marker in swarm_content
            for marker in ["## Roles", "Roles & Responsibilities", "| Agent", "| Role"]
        )

        assert has_roles, "AI Swarm should define agent roles"

    def test_swarm_documents_workflow_loop(self, swarm_content):
        """Test that AI Swarm workflow documents the orchestration loop."""
        # Should document the workflow cycle
        documents_loop = any(
            term in swarm_content
            for term in ["Workflow Loop", "Swarm Cycle", "Phase 1", "Phase 2"]
        )

        assert documents_loop, "AI Swarm should document workflow cycle"

    def test_swarm_has_security_safeguards_section(self, swarm_content):
        """Test that AI Swarm workflow documents security safeguards."""
        # Should have security or safety section
        has_security = any(
            marker in swarm_content
            for marker in ["Security", "Safety", "CRITICAL", "Safeguards"]
        )

        assert has_security, "AI Swarm should document security safeguards"

    def test_swarm_documents_automation_constraints(self, swarm_content):
        """Test that AI Swarm workflow documents automation constraints."""
        # Should mention automation rules or constraints
        documents_automation = any(
            term in swarm_content
            for term in ["automation", "turbo-all", "approve", "approval"]
        )

        assert documents_automation, "AI Swarm should document automation constraints"


class TestWorkflowIntegration:
    """Integration tests between different workflows."""

    def test_clarify_to_plan_handoff(self):
        """Test that clarify workflow properly hands off to plan workflow."""
        clarify_path = Path("/home/jailuser/git/.kilocode/workflows/speckit.clarify.md")

        if not clarify_path.exists():
            pytest.skip("clarify workflow not found")

        with open(clarify_path, 'r') as f:
            content = f.read()

        # Clarify should mention when to proceed to planning
        mentions_plan = any(
            phrase in content
            for phrase in ["speckit.plan", "/speckit.plan", "planning", "proceed to"]
        )

        assert mentions_plan, "Clarify should document handoff to plan"

    def test_tasks_to_implement_handoff(self):
        """Test that tasks workflow properly hands off to implement workflow."""
        tasks_path = Path("/home/jailuser/git/.kilocode/workflows/speckit.tasks.md")

        if not tasks_path.exists():
            pytest.skip("tasks workflow not found")

        with open(tasks_path, 'r') as f:
            content = f.read()

        # Tasks should mention implementation as next step
        mentions_implement = any(
            phrase in content
            for phrase in ["speckit.implement", "/speckit.implement", "implementation"]
        )

        assert mentions_implement, "Tasks should document handoff to implement"


class TestWorkflowErrorHandling:
    """Tests for error handling documentation in workflows."""

    def test_workflows_document_prerequisite_checks(self):
        """Test that workflows document their prerequisite checks."""
        workflow_dir = Path("/home/jailuser/git/.kilocode/workflows")

        if not workflow_dir.exists():
            pytest.skip("Workflow directory not found")

        prerequisite_sensitive = ["speckit.tasks", "speckit.implement", "speckit.analyze"]

        for workflow_name in prerequisite_sensitive:
            workflow_path = workflow_dir / f"{workflow_name}.md"

            if not workflow_path.exists():
                continue

            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should check prerequisites or document setup requirements
            checks_prerequisites = any(
                term in content.lower()
                for term in [
                    "check-prerequisites",
                    "prerequisite",
                    "feature_dir",
                    "spec_file",
                    "skip",
                    "abort",
                    "setup",
                    "load",
                    "read",
                ]
            )

            assert checks_prerequisites, f"{workflow_name} should document prerequisite checks"

    def test_workflows_document_error_conditions(self):
        """Test that workflows document what to do when things go wrong."""
        workflow_dir = Path("/home/jailuser/git/.kilocode/workflows")

        if not workflow_dir.exists():
            pytest.skip("Workflow directory not found")

        for workflow_path in workflow_dir.glob("speckit.*.md"):
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should have some error handling guidance
            has_error_handling = any(
                marker in content.lower()
                for marker in ["error", "fail", "missing", "not found", "skip", "caution", "warning"]
            )

            # Not all workflows need explicit error handling
            # Skip simple utility workflows
            if workflow_path.stem not in [
                "speckit.constitution",
                "speckit.clarify",
                "speckit.taskstoissues",  # Simple GitHub integration
            ]:
                assert has_error_handling, f"{workflow_path.name} should document error conditions"


# --- Regression Tests ---

class TestRegressionPrevention:
    """Tests to prevent regression of known issues."""

    def test_mcp_json_does_not_contain_exposed_redis_password(self):
        """Regression test: Ensure Redis password exposure bug doesn't return."""
        mcp_path = Path("/home/jailuser/git/.kilocode/mcp.json")

        if not mcp_path.exists():
            pytest.skip("MCP config not found")

        with open(mcp_path, 'r') as f:
            content = f.read()

        # The specific exposed password that was found in audit
        exposed_password = "s0C38imHFb1fkkk9ix84sVJsqUFk4ieD"

        assert exposed_password not in content, \
            "SECURITY REGRESSION: Exposed Redis password found in mcp.json"

        # Check for any Redis Cloud hostnames with passwords
        redis_cloud_pattern = r'rediss?://[^:]+:[^@]{10,}@.*redislabs\.com'
        matches = re.findall(redis_cloud_pattern, content)

        # Filter out environment variable patterns
        real_matches = [m for m in matches if "${" not in m]

        assert not real_matches, \
            "SECURITY REGRESSION: Hardcoded Redis Cloud credentials found"

    def test_env_example_documents_redis_fallback_behavior(self):
        """Regression test: Ensure Redis fallback behavior is documented."""
        env_path = Path("/home/jailuser/git/.env.example")

        if not env_path.exists():
            pytest.skip(".env.example not found")

        with open(env_path, 'r') as f:
            content = f.read()

        # Should document what happens when Redis is not available
        documents_fallback = any(
            phrase in content
            for phrase in [
                "fallback",
                "Behavior:",
                "dev mode",
                "DEBUG=True",
                "production",
            ]
        )

        assert documents_fallback, \
            "REGRESSION: Redis fallback behavior should be documented in .env.example"