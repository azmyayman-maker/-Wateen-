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
