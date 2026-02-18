# Data Model: Post-Audit Codebase Cleanup & Fixes

**Branch**: `001-audit-cleanup` | **Date**: 2026-02-19

## Overview

This feature does not introduce any data model changes. It is a remediation task focused on code quality, security, and test reliability.

## Existing Entities (Unchanged)

The following entities exist in the codebase and remain unchanged:

| Entity | Location | Description |
|--------|----------|-------------|
| User | `users/models.py` | Django User model with custom fields |
| PatientProfile | `users/models.py` | Patient-specific profile |
| NurseProfile | `users/models.py` | Nurse-specific profile with location |
| Visit | `visits/models.py` | Visit request with location, status |
| VisitStatus | `visits/models.py` | Enum for visit states |
| ServiceType | `visits/models.py` | Types of medical services |
| PricingFactor | `visits/models.py` | Configurable pricing multipliers |

## Data Model Changes

**None required.**

This task modifies:
- Utility scripts (no data model)
- Configuration files (no data model)
- Service logic (behavioral changes only)
- Tests (no data model)

## Database Migrations

**None required.**

No schema changes are part of this remediation.
