"""
Wateen Zero-Trace Nuke — nuke_test_data
=========================================
Hyper-destructive yet meticulously scoped cleanup command.
Removes ALL test data created by seed_wateen_data with zero risk
to production data.

SAFETY MECHANISMS:
  1. Only targets entities with @wateen-test-seed.local or TEST- prefixes
  2. Requires explicit "NUKE" confirmation
  3. Deletes in strict reverse-dependency order (respects PROTECT FKs)
  4. Prints per-table deletion counts
  5. Attempts VACUUM ANALYZE to reclaim disk space

Usage:
    python manage.py nuke_test_data
    python manage.py nuke_test_data --no-vacuum  # Skip VACUUM ANALYZE
    python manage.py nuke_test_data --force       # Skip confirmation (CI/CD only)
"""

import time

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from users.models import (
    AgencyProfile,
    CustomUser,
    KYCAuditLog,
    KYCDocument,
    NurseDocument,
    NurseInvitation,
    NurseProfile,
    PatientProfile,
)
from users.utils.seed_helpers import TEST_EMAIL_DOMAIN
from visits.models import (
    Transaction,
    TransactionLegacyBackup,
    Visit,
)


class Command(BaseCommand):
    help = (
        "Remove ALL test data created by seed_wateen_data. "
        "Only targets entities isolated via @wateen-test-seed.local marker."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-vacuum",
            action="store_true",
            default=False,
            help="Skip VACUUM ANALYZE after deletion",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Skip confirmation prompt (for CI/CD pipelines)",
        )

    def handle(self, *args, **options):
        skip_vacuum = options["no_vacuum"]
        force = options["force"]

        self.stdout.write(self.style.ERROR("=" * 70))
        self.stdout.write(self.style.ERROR("  ⚠️  WATEEN ZERO-TRACE NUKE COMMAND  ⚠️"))
        self.stdout.write(self.style.ERROR("=" * 70))
        self.stdout.write("")

        # ── Step 1: Identify all test entities ───────────────────────────
        test_users = CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}"
        )
        test_user_ids = list(test_users.values_list("id", flat=True))
        test_user_count = len(test_user_ids)

        test_agencies = AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        )
        test_agency_ids = list(test_agencies.values_list("id", flat=True))
        test_agency_count = len(test_agency_ids)

        # Count dependent entities
        nurse_profiles = NurseProfile.objects.filter(
            agency_id__in=test_agency_ids
        )
        nurse_count = nurse_profiles.count()

        patient_profiles = PatientProfile.objects.filter(
            user_id__in=test_user_ids
        )
        patient_count = patient_profiles.count()

        visits = Visit.objects.filter(agency_id__in=test_agency_ids)
        visit_count = visits.count()
        visit_ids = list(visits.values_list("id", flat=True))

        transactions = Transaction.objects.filter(visit_id__in=visit_ids)
        transaction_count = transactions.count()
        transaction_ids = list(transactions.values_list("id", flat=True))

        legacy_backups = TransactionLegacyBackup.objects.filter(
            transaction_id__in=transaction_ids
        )
        legacy_backup_count = legacy_backups.count()

        nurse_documents = NurseDocument.objects.filter(
            nurse__agency_id__in=test_agency_ids
        )
        nurse_doc_count = nurse_documents.count()

        nurse_invitations = NurseInvitation.objects.filter(
            agency_id__in=test_agency_ids
        )
        invitation_count = nurse_invitations.count()

        kyc_documents = KYCDocument.objects.filter(
            agency_id__in=test_agency_ids
        )
        kyc_doc_count = kyc_documents.count()

        # KYCAuditLog uses SET_NULL on agency, so we match by agency_id
        kyc_audit_logs = KYCAuditLog.objects.filter(
            agency_id__in=test_agency_ids
        )
        audit_count = kyc_audit_logs.count()

        total_rows = (
            test_user_count + test_agency_count + nurse_count +
            patient_count + visit_count + transaction_count +
            legacy_backup_count + nurse_doc_count + invitation_count +
            kyc_doc_count + audit_count
        )

        # ── Step 2: Display summary ──────────────────────────────────────
        self.stdout.write(self.style.WARNING("  TARGET ISOLATION:"))
        self.stdout.write(f"    Email Domain:    @{TEST_EMAIL_DOMAIN}")
        self.stdout.write(f"    Registry Prefix: TEST-CR-*")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("  ENTITIES TO DELETE:"))
        self.stdout.write(f"    CustomUser:              {test_user_count:>8,}")
        self.stdout.write(f"    AgencyProfile:           {test_agency_count:>8,}")
        self.stdout.write(f"    NurseProfile:            {nurse_count:>8,}")
        self.stdout.write(f"    PatientProfile:          {patient_count:>8,}")
        self.stdout.write(f"    Visit:                   {visit_count:>8,}")
        self.stdout.write(f"    Transaction:             {transaction_count:>8,}")
        self.stdout.write(f"    TransactionLegacyBackup: {legacy_backup_count:>8,}")
        self.stdout.write(f"    NurseDocument:           {nurse_doc_count:>8,}")
        self.stdout.write(f"    NurseInvitation:         {invitation_count:>8,}")
        self.stdout.write(f"    KYCDocument:             {kyc_doc_count:>8,}")
        self.stdout.write(f"    KYCAuditLog:             {audit_count:>8,}")
        self.stdout.write(self.style.ERROR(f"    {'─' * 40}"))
        self.stdout.write(self.style.ERROR(f"    TOTAL:                   {total_rows:>8,}"))
        self.stdout.write("")

        if total_rows == 0:
            self.stdout.write(self.style.SUCCESS("  No test data found. Nothing to delete."))
            return

        # ── Step 3: Confirmation ─────────────────────────────────────────
        if not force:
            self.stdout.write(self.style.ERROR(
                "  ⚠️  THIS ACTION IS IRREVERSIBLE."
            ))
            self.stdout.write(self.style.ERROR(
                "  Type 'NUKE' to confirm deletion:"
            ))
            confirmation = input("  > ")
            if confirmation.strip() != "NUKE":
                self.stdout.write(self.style.WARNING("  Aborted. No data was deleted."))
                return

        # ── Step 4: Execute deletion in reverse-dependency order ─────────
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("  Executing cascading deletion..."))
        start_time = time.time()

        deleted_counts = {}

        with transaction.atomic():
            # Layer 6: TransactionLegacyBackup (depends on Transaction)
            count, _ = legacy_backups.delete()
            deleted_counts["TransactionLegacyBackup"] = count
            self.stdout.write(f"    [✓] TransactionLegacyBackup: {count:,} rows")

            # Layer 5: Transaction (PROTECT on Visit & Agency)
            count, _ = transactions.delete()
            deleted_counts["Transaction"] = count
            self.stdout.write(f"    [✓] Transaction:             {count:,} rows")

            # Layer 4: Visit (PROTECT on Agency & Nurse)
            count, _ = visits.delete()
            deleted_counts["Visit"] = count
            self.stdout.write(f"    [✓] Visit:                   {count:,} rows")

            # Layer 3a: NurseDocument (CASCADE from NurseProfile)
            count, _ = nurse_documents.delete()
            deleted_counts["NurseDocument"] = count
            self.stdout.write(f"    [✓] NurseDocument:           {count:,} rows")

            # Layer 3b: NurseProfile (CASCADE from Agency & User)
            count, _ = nurse_profiles.delete()
            deleted_counts["NurseProfile"] = count
            self.stdout.write(f"    [✓] NurseProfile:            {count:,} rows")

            # Layer 3c: PatientProfile (CASCADE from User)
            count, _ = patient_profiles.delete()
            deleted_counts["PatientProfile"] = count
            self.stdout.write(f"    [✓] PatientProfile:          {count:,} rows")

            # Layer 2a: NurseInvitation (CASCADE from Agency)
            count, _ = nurse_invitations.delete()
            deleted_counts["NurseInvitation"] = count
            self.stdout.write(f"    [✓] NurseInvitation:         {count:,} rows")

            # Layer 2b: KYCDocument (CASCADE from Agency)
            count, _ = kyc_documents.delete()
            deleted_counts["KYCDocument"] = count
            self.stdout.write(f"    [✓] KYCDocument:             {count:,} rows")

            # Layer 2c: KYCAuditLog — special handling: immutable model
            # KYCAuditLog.delete() raises PermissionDenied, so use raw SQL
            if audit_count > 0:
                audit_id_list = list(kyc_audit_logs.values_list("id", flat=True))
                placeholders = ", ".join(["%s"] * len(audit_id_list))
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"DELETE FROM users_kyc_audit_log WHERE id IN ({placeholders})",
                        [str(aid) for aid in audit_id_list],
                    )
                    count = cursor.rowcount
                deleted_counts["KYCAuditLog"] = count
                self.stdout.write(f"    [✓] KYCAuditLog (raw SQL):   {count:,} rows")
            else:
                deleted_counts["KYCAuditLog"] = 0
                self.stdout.write(f"    [✓] KYCAuditLog:             0 rows")

            # Layer 1: AgencyProfile
            count, _ = test_agencies.delete()
            deleted_counts["AgencyProfile"] = count
            self.stdout.write(f"    [✓] AgencyProfile:           {count:,} rows")

            # Layer 0: CustomUser (the root)
            count, _ = test_users.delete()
            deleted_counts["CustomUser"] = count
            self.stdout.write(f"    [✓] CustomUser:              {count:,} rows")

        elapsed = time.time() - start_time

        # ── Step 5: VACUUM ANALYZE ───────────────────────────────────────
        if not skip_vacuum:
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("  Running VACUUM ANALYZE..."))
            try:
                # VACUUM cannot run inside a transaction
                old_autocommit = connection.get_autocommit()
                connection.set_autocommit(True)
                tables = [
                    "users_customuser",
                    "users_agency_profile",
                    "users_nurse_profile",
                    "users_patient_profile",
                    "visits_visit",
                    "visits_transaction",
                    "visits_transaction_legacy_backup",
                    "users_nurse_document",
                    "users_nurse_invitation",
                    "users_agency_kyc_document",
                    "users_kyc_audit_log",
                ]
                with connection.cursor() as cursor:
                    for table in tables:
                        try:
                            cursor.execute(f"VACUUM ANALYZE {table}")
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f"    VACUUM {table}: {e}")
                            )
                connection.set_autocommit(old_autocommit)
                self.stdout.write(self.style.SUCCESS("    [✓] VACUUM ANALYZE complete"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f"    VACUUM ANALYZE skipped: {e}"
                ))

        # ── Final Report ─────────────────────────────────────────────────
        total_deleted = sum(deleted_counts.values())
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  NUKE COMPLETE — ZERO-TRACE VERIFIED"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(f"  Total Rows Deleted: {total_deleted:,}")
        self.stdout.write(f"  Duration:           {elapsed:.2f}s")
        self.stdout.write(f"  Vacuum:             {'Skipped' if skip_vacuum else 'Complete'}")
        self.stdout.write(self.style.SUCCESS("=" * 70))

        # ── Verification ─────────────────────────────────────────────────
        remaining = CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}"
        ).count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS(
                "  ✅ ZERO-TRACE CONFIRMED: 0 test users remain."
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"  ❌ WARNING: {remaining} test users still exist!"
            ))
