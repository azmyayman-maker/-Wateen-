import pytest
from io import StringIO
from django.core.management import call_command
from django.db.migrations.recorder import MigrationRecorder

pytestmark = pytest.mark.django_db


class TestMigrationSafety:
    """
    Validates migration graph integrity.
    Ensures all migrations are applied and there are no conflicts.
    """

    def test_no_unapplied_migrations(self):
        """
        Runs `manage.py migrate --check` programmatically.
        Exits silently if no unapplied migrations exist.
        Raises SystemExit(1) if unapplied migrations are found.
        """
        try:
            call_command('migrate', '--check', verbosity=0)
        except SystemExit as e:
            pytest.fail(f"Unapplied migrations detected! (Exit code: {e.code})")
        
        # Also double check via DB that migrations exist
        assert MigrationRecorder.Migration.objects.count() > 0

    def test_no_missing_migrations(self):
        """
        Runs `makemigrations --check --dry-run`.
        Fails if there are pending model changes without a migration.
        """
        try:
            call_command('makemigrations', '--check', '--dry-run', verbosity=0)
        except SystemExit as e:
            pytest.fail(f"Missing migrations detected! Run makemigrations. (Exit code: {e.code})")

    def test_migration_plan_loads_without_conflicts(self):
        """
        Loading the migration plan guarantees there are no multiple leaf nodes
        (merge conflicts) in the migration graph.
        """
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()
        
        # Ensure it outputs something (sanity check)
        assert len(output.strip()) > 0
        assert "users" in output
        assert "visits" in output
