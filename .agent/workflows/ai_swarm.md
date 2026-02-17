---
description: Standard operating procedure for the "AI Swarm" workflow where Antigravity manages OpenCode (Builder) and Kilo Code (Reviewer).
---

# AI Swarm Orchestration Protocol (Reversed)

This workflow defines the **MANDATORY** standard operating procedure for all tasks in this workspace.

## 1. Roles & Responsibilities

| Agent                | Role                      | Responsibilities                                                                                        | Tools/Access                                       |
| :------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------- |
| **Antigravity (Me)** | **Manager / Architect**   | High-level planning, task breakdown, prompt generation, triggering OpenCode, synthesizing Kilo reviews. | File System, MCPs, `opencode` CLI.                 |
| **OpenCode**         | **Builder / Implementer** | Writing professional, secure code based on specifications.                                              | `opencode` CLI (Automated/Managed by Antigravity). |
| **Kilo Code**        | **Reviewer / QA**         | Professional Code Review, Security Audit, Technical & Security Feedback.                                | VS Code Extension / CLI (via User).                |

## 2. Directory Structure

```text
.agent/
├── planning/          # High-level implementation plans (Antigravity)
├── tasks/             # Specific prompts for OpenCode (Antigravity)
│   ├── pending/       # Tasks waiting for execution
│   └── completed/     # Tasks finished by OpenCode
├── reviews-qa/        # Audit reports from Kilo Code (User/Kilo)
└── logs/              # Execution logs
```

## 3. Workflow Loop (The "Swarm Cycle")

### Phase 1: Planning (Antigravity)

1.  **Analyze Request:** Understand the user's goal.
2.  **Create Plan:** Write/Update `implementation_plan.md`.
3.  **Generate Task:** Create a prompt file `.agent/tasks/pending/task_XXX.md`.

### Phase 2: Execution (OpenCode - Automated)

1.  **Trigger:** Antigravity runs OpenCode CLI.
    - _Command:_ `opencode --prompt-file .agent/tasks/pending/task_XXX.md`
2.  **Action:** OpenCode implements the changes.
3.  **Completion:** Antigravity verifies file creation.

### Phase 3: Review (Kilo Code - User/Manual)

1.  **Trigger:** User asks Kilo Code to review.
    - _Prompt to Kilo:_ "Review the changes in [files] based on `.agent/tasks/pending/task_XXX.md`. Save report to `.agent/reviews-qa/review_XXX.md`."
2.  **Action:** Kilo Code analyzes and writes the report.

### Phase 4: Synthesis (Antigravity)

1.  **Analyze:** Antigravity reads the review report.
2.  **Refine:** If issues are found, Antigravity creates a remediation task for OpenCode (Repeat Phase 2).

## 4. How to Run This Protocol

1.  **To Start a Task:** Just ask Antigravity (me). I will plan and trigger OpenCode.
2.  **To Review:** When I say "Build Complete", you (User) run Kilo Code to review.
3.  **To Finish:** Provide the Kilo Code review output to me.

## 5. Automation Tags

// turbo-all
(This workflow authorizes auto-running `opencode` CLI commands for building).

## 6. Security & Safety

**CRITICAL:** The `turbo-all` automation tag MUST NOT be enabled without the following safeguards:

### 6.1 Security Review Requirement
- A security review MUST be completed and documented before enabling any automation.
- Review findings must be addressed and sign-off obtained from at least one designated maintainer.

### 6.2 Prompt File Validation
- All prompt files in `.agent/tasks/pending/` MUST be validated against the defined schema.
- Invalid or malformed prompt files MUST be rejected before execution.

### 6.3 Access Control
- Only designated maintainers (listed in `.agent/MAINTAINERS`) may add or modify the `turbo-all` tag.
- Unauthorized modifications to automation tags MUST be rejected and logged.

### 6.4 Execution Environment
- OpenCode MUST run in a sandboxed/restricted execution environment.
- File system access MUST be scoped to the project directory only.
- Network access MUST be explicitly whitelisted per task requirement.

### 6.5 Audit Logging
- All automated actions MUST be recorded to `.agent/logs/audit.log`.
- Log entries MUST include: timestamp, agent, action, files modified, and outcome.

### 6.6 Manual Approval Gates & Rate Limiting
- High-risk operations (e.g., deletions, external API calls, privilege changes) MUST require manual approval.
- Rate limiting MUST be enforced: max 10 automated actions per hour, with exponential backoff on failures.
- Runaway automation detection: halt after 3 consecutive failures and alert maintainers.
