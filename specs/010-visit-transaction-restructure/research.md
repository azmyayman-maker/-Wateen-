# Research: Visit & Transaction Model Restructuring

**Feature**: 010-visit-transaction-restructure  
**Date**: 2026-03-01

## Decision 1: Foreign Key Deletion Strategy

- **Decision**: Use `on_delete=PROTECT` for Visit→Agency, Visit→Nurse, Transaction→Visit, Transaction→Agency
- **Rationale**: Financial records must never be orphaned. `PROTECT` prevents deletion of agencies/nurses that have associated visits, preserving referential integrity for audits and disputes. `SET_NULL` (current) would silently break the financial chain.
- **Alternatives considered**: `SET_NULL` (current — loses audit trail), `CASCADE` (deletes visits when agency deleted — catastrophic data loss), `RESTRICT` (similar to PROTECT but with subtle timing differences in Django's deletion cascade)

## Decision 2: Pricing Immutability Enforcement Layer

- **Decision**: Enforce at Django model `save()` override by comparing against database values via `Visit.objects.get(pk=self.pk)`
- **Rationale**: Application-layer enforcement is sufficient for this stage. Database-level triggers add operational complexity (PostgreSQL triggers) without additional safety given that all mutations go through Django ORM.
- **Alternatives considered**: PostgreSQL triggers (heavier, harder to test/maintain), Django signals (pre_save — same layer, less explicit), `clean()` override (not called by ORM bulk operations or `save()` without `full_clean()`)

## Decision 3: Payment Gateway

- **Decision**: Paymob (replace Stripe references)
- **Rationale**: Paymob has full Egyptian market support with local card networks, mobile wallets (Vodafone Cash, Fawry), and EGP settlement. Stripe Connect has limited Egypt availability.
- **Alternatives considered**: Stripe Connect (limited Egypt support, USD settlement), Tap Payments (MENA-focused but less Egyptian coverage), Fawry direct (payment only, no escrow)

## Decision 4: Transaction Status Lifecycle

- **Decision**: Three states only: `ESCROWED` → `SETTLED` | `REFUNDED`. Remove `PENDING` and `FAILED`.
- **Rationale**: Since Transactions are only created at payment capture (Q1 clarification), there is no "pending" pre-payment state. Payment failures are Paymob-level events that don't create ledger entries.
- **Alternatives considered**: Keep `PENDING` (would create Transaction records before payment confirmation — unnecessary complexity), keep `FAILED` (payment gateway failure doesn't create a financial ledger entry)

## Decision 5: Data Migration Strategy

- **Decision**: Data-preserving `RenameField` migrations for direct renames; `AddField` + data migration for field splits
- **Rationale**: Active development may have test/staging data worth preserving. `RenameField` creates clean audit trail in migration history.
- **Alternatives considered**: Destructive (add/drop — data loss), keep old names (confusion, technical debt)

## Decision 6: Surge Coefficient Field Naming

- **Decision**: Keep `ai_surge_coefficient` (existing name) rather than renaming to `surge_coefficient`
- **Rationale**: The existing name is more descriptive (indicates AI/ML calculation source) and aligns with the user's implementation plan. Renaming would require migration with no functional benefit.
- **Alternatives considered**: `surge_coefficient` (as specified in ticket — shorter but less descriptive), `surge_multiplier` (conflicts with `ServiceType.surge_multiplier`)
