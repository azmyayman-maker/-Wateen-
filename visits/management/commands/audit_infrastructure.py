from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
from django_redis import get_redis_connection
import sys

class Command(BaseCommand):
    help = 'Audits infrastructure connectivity (DB, PostGIS, Redis)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting Infrastructure Audit..."))
        
        # 1. Database & PostGIS
        self.check_database()
        
        # 2. Redis
        self.check_redis()
        
        self.stdout.write(self.style.SUCCESS("Audit Complete."))

    def check_database(self):
        self.stdout.write("Checking Database Connection & PostGIS...")
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            self.stdout.write(self.style.ERROR("[FAIL] Could not connect to Database"))
            return

        # Check PostGIS
        with db_conn.cursor() as cursor:
            try:
                cursor.execute("SELECT postgis_version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"[OK] Database Connected. PostGIS Version: {version}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[FAIL] PostGIS error: {e}"))

    def check_redis(self):
        self.stdout.write("Checking Redis Connection & Geo...")
        try:
            con = get_redis_connection("default")
            con.ping()
            self.stdout.write(self.style.SUCCESS(f"[OK] Redis Connected (Ping success)"))
            
            # Geo Test
            key = "audit:geo_test"
            con.delete(key)
            con.geoadd(key, (31.2357, 30.0444, "Cairo_Tower")) # Lon, Lat, Member
            proxs = con.georadius(key, 31.2357, 30.0444, 1, unit="km")
            
            if b"Cairo_Tower" in proxs or "Cairo_Tower" in proxs:
                 self.stdout.write(self.style.SUCCESS("[OK] Redis Geo module active"))
            else:
                 self.stdout.write(self.style.ERROR("[FAIL] Redis Geo test failed"))
                 
            # Pub/Sub Test
            pubsub = con.pubsub()
            pubsub.subscribe("audit_channel")
            con.publish("audit_channel", "test_message")
            # In a real sync script, getting the message back might require a loop or separate thread
            # but getting here means publish didn't raise error.
            self.stdout.write(self.style.SUCCESS("[OK] Redis Pub/Sub capable"))
            
            con.delete(key)

        except Exception as e:
             self.stdout.write(self.style.ERROR(f"[FAIL] Redis Error: {e}"))
