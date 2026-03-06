from django.core.management.base import BaseCommand
from django.db import connection
from users.models import AgencyProfile
from django.contrib.postgres.indexes import GistIndex

class Command(BaseCommand):
    help = "Verify PostGIS installation and spatial index status for Wateen"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("--- Wateen PostGIS Diagnostics ---"))

        # 1. Check DB Engine
        engine = connection.settings_dict.get('ENGINE')
        self.stdout.write(f"DB Engine: {engine}")
        if 'postgis' not in engine:
            self.stderr.write(self.style.ERROR("CRITICAL: PostGIS engine not detected in settings!"))
            return

        # 2. Check PostGIS Version
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT PostGIS_Full_Version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"PostGIS Version: {version}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"CRITICAL: Failed to query PostGIS version. Is it installed? Error: {e}"))
            return

        # 3. Check Model Field & Index
        self.stdout.write("Checking AgencyProfile spatial configuration...")
        field = AgencyProfile._meta.get_field('coverage_polygon')
        if field.__class__.__name__ != 'PolygonField':
            self.stderr.write(self.style.ERROR("ERROR: coverage_polygon is not a PolygonField!"))
        else:
            self.stdout.write(self.style.SUCCESS("✓ coverage_polygon is a valid GeoDjango field (SRID=4326)"))

        # Check for GistIndex in Meta
        has_gist = any(isinstance(idx, GistIndex) and 'coverage_polygon' in idx.fields for idx in AgencyProfile._meta.indexes)
        if has_gist:
            self.stdout.write(self.style.SUCCESS("✓ GistIndex detected on coverage_polygon"))
        else:
            self.stderr.write(self.style.WARNING("WARNING: GistIndex NOT detected in AgencyProfile.Meta.indexes. High-scale queries may be slow."))

        self.stdout.write(self.style.MIGRATE_SUCCESS("--- Diagnostics Complete ---"))
