---
description: PROFESSIONAL TASK SPECIFICATION TEMPLATE (AGENT-EXECUTABLE FORMAT)
---

Task Identification

Task ID: [Task ID]
Task Name: [Task Name]

Status: Pending
Assigned Execution Agent: OpenCode
Assigned Review Authority: Kilo Code

1) Context & Objective

Provide a concise but technically precise description of the purpose of this task.

The description must clarify:

The functional goal of the task

The technical problem being solved

The role of this task within the larger system

The expected system behavior after completion

The explanation must be sufficient for an implementation agent to understand the intent without external clarification.

2) Technical Specifications
Target Files

List every file that will be created, modified, or referenced.

Include:

Absolute or project-relative paths

File responsibility

Whether the file is new or existing

Architecture Rules

All implementation must strictly follow Wateen Architecture constraints, including:

Proper separation of responsibilities

Respecting service layers

Avoiding business logic in forbidden layers

Maintaining module boundaries

Preventing implicit coupling

Any deviation is considered a task failure.

Technology Stack

Specify all tools, frameworks, and runtime environments required for the task, for example:

Backend framework(s)

Frontend framework(s)

Database

External services

Supporting libraries

Versions must be specified when relevant.

3) Implementation Steps

Provide a deterministic ordered checklist.

Each step must:

Represent a concrete action

Be verifiable

Avoid ambiguity

Not combine multiple logical actions

Example structure:

 Step 1 — Description

 Step 2 — Description

 Step N — Description

The execution agent must follow the steps sequentially.

4) Definition of Done (DoD)

The task is considered complete only when ALL conditions are satisfied.

Functional Validation

Code compiles and runs without runtime errors

All expected behaviors operate correctly

No regression introduced

Architectural Compliance

Fully compliant with Wateen architecture

No layer violations

No hidden dependencies

Standards Compliance

Fully compliant with .cursorrules

Naming and structure consistent with project conventions

5) Acceptance Authority

The Reviewer (Kilo Code) must validate:

Correctness

Architectural integrity

Stability

Maintainability

Failure in any category rejects the task.

Final Directive

The execution agent must not deviate from this specification.
The reviewer must reject the task if any section is partially satisfied.