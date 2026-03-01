# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: Django 5.2, Django REST Framework, PostGIS 3.4  
**Storage**: PostgreSQL 16 + PostGIS  
**Testing**: pytest  
**Target Platform**: Linux server (Dockerized)  
**Project Type**: web-service (Backend API)  
**Performance Goals**: Sub 200ms API response times.  
**Constraints**: Ensure strict multi-tenant data isolation; `transaction.atomic` MUST be used.  
**Scale/Scope**: Covers invitation flow and registration for B2B2C agencies.

## Constitution Check

_GATE: Passed_

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/009-nurse-invitation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
users/
├── models.py
├── nurse_serializers.py
├── nurse_views.py
└── urls.py
```

**Structure Decision**: Option 1: Single project (DEFAULT). All modifications strictly placed in the `users` app.

## Complexity Tracking

| Violation         | Why Needed                                  | Simpler Alternative Rejected Because                           |
| ----------------- | ------------------------------------------- | -------------------------------------------------------------- |
| Custom validation | B2B2C architecture enforces IDOR strictness | Relying on generic `ModelSerializer` is unsafe across agencies |
