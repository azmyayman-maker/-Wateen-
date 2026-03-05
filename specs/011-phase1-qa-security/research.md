# Research: Phase 1 QA, Security & Validation

**Date**: 2026-03-01 | **Branch**: `011-phase1-qa-security`

## R1: NurseProfile Agency FK Enforcement

**Decision**: NurseProfile.agency is a non-nullable ForeignKey at the DB level (no `null=True`).
**Rationale**: The model definition at `users/models.py:379-385` defines `agency = models.ForeignKey("AgencyProfile", on_delete=models.CASCADE)` without `null=True`. Django generates a NOT NULL constraint on `agency_id` column. Additionally, `NurseProfile.clean()` (line 452) raises `ValidationError` if `agency_id` is falsy, and `save()` calls `full_clean()` by default.
**Alternatives Considered**: CheckConstraint was considered (commented out at line 439-444) but the FK NOT NULL is sufficient since Django ForeignKey without `null=True` already enforces this at the DB schema level.

## R2: PostGIS Polygon Validation

**Decision**: PostgreSQL/PostGIS validates geometry on INSERT. Invalid geometries (self-intersecting, unclosed rings) raise `GEOSException` or `InternalError`.
**Rationale**: The `coverage_polygon` field is `gis_models.PolygonField(srid=4326, null=True, blank=True)`. PostGIS validates that the geometry is a valid polygon. A `LinearRing` with < 4 points or an unclosed ring will cause a GEOS error at the ORM level before it even hits the DB. Self-intersecting polygons may be accepted by PostGIS but fail `ST_IsValid()`.
**Alternatives Considered**: Application-level polygon validation was considered but DB-level enforcement via PostGIS is more reliable and cannot be bypassed.

## R3: RBAC Permission Classes

**Decision**: 5 DRF permission classes in `users/permissions.py` guard all protected endpoints.
**Rationale**: After analyzing all views:

- `InviteNurseView` uses `IsAuthenticated, IsAgencyAdmin` — NURSE role will get 403
- `ManualDispatchView` uses `IsAuthenticated, IsAgencyAdminOrSuperAdmin` — PATIENT role will get 403
- Visit serializers (`VisitResponseSerializer`) use read-only fields, so PATCH with `base_price`/`final_price` will be silently ignored
  **Alternatives Considered**: None — DRF permission classes are the standard pattern.

## R4: Visit Financial Field Protection

**Decision**: `base_price` and `final_price` are NOT in any input serializer. The `VisitRequestSerializer` only accepts `latitude`, `longitude`, and `service_type`. Financial fields are set server-side during visit creation.
**Rationale**: Reviewed `visits/serializers.py` — no ModelSerializer exposes Visit model directly. All serializers are plain `Serializer` classes with explicitly declared fields. There is no `PATCH` endpoint for Visit that accepts arbitrary fields.
**Alternatives Considered**: Could add explicit `read_only_fields` meta but plain Serializer classes don't auto-include model fields, so this is already secure by default.

## R5: Static Analysis Tooling

**Decision**: Use `ruff check .` for linting and `mypy users/ visits/ --ignore-missing-imports` for type checking.
**Rationale**: `ruff` is already configured (`.ruff_cache` dir exists). `mypy` should target only Phase 1 apps (`users/`, `visits/`) since `config/`, `tests/`, and third-party code may have unresolvable type issues.
**Alternatives Considered**: Full `mypy .` was considered but would surface issues in Django internals and third-party packages outside our control.

## R6: Migration Safety Testing

**Decision**: Use `call_command('migrate', '--check')` in a pytest test and run `showmigrations --plan` to verify no conflicts.
**Rationale**: Django's `--check` flag exits with non-zero if unapplied migrations exist. This is the official CI-ready check. `showmigrations --plan` with `--list` reveals merge conflicts.
**Alternatives Considered**: `makemigrations --check` could also be used but checks for missing migrations rather than unapplied ones — both are valuable.
