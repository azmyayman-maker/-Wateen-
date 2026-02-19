import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.contrib.gis.geos import Point

# Setup Django environment
sys.path.append("/app")  # Adjust as needed if not in root
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from visits.models import Visit, VisitStatus
from users.models import PatientProfile, UserRole

User = get_user_model()


def verify_postgis():
    print("Verifying PostGIS extension...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT postgis_version();")
        row = cursor.fetchone()
        if row:
            print(f"PostGIS Version: {row[0]}")
            return True
        else:
            print("FAILED: PostGIS version not returned.")
            return False


def verify_crud():
    print("Verifying Visit CRUD operations...")
    user = None
    visit = None
    try:
        # 1. Create User (Patient)
        # Valid ID: 2 (1900-1999) + 900101 (DOB) + 01 (Cairo) + 000 (Seq) + 3 (Check)
        national_id = "29001010100003"
        import random

        # Random phone to avoid collision: 010 + 8 digits
        phone = f"010{random.randint(10000000, 99999999)}"

        # Cleanup if exists (idempotency)
        User.objects.filter(national_id=national_id).delete()
        User.objects.filter(phone_number=phone).delete()

        user = User.objects.create_user(
            national_id=national_id,
            phone_number=phone,
            password="testpassword123",
            role=UserRole.PATIENT,
        )
        print(f"Created User: {user.national_id}")

        # 2. Get Patient Profile (created by signal)
        profile = PatientProfile.objects.get(user=user)
        print(f"Retrieved PatientProfile: {profile}")

        # 3. Create Visit
        # GeoDjango Point expects (longitude, latitude) order
        # Cairo coordinates: lon=31.2357, lat=30.0444
        location = Point(31.2357, 30.0444)  # (lon, lat) - GeoDjango standard
        visit = Visit.objects.create(
            patient=profile, location=location, status=VisitStatus.PENDING
        )
        print(f"Created Visit: {visit.id}")

        # 4. Read
        retrieved_visit = Visit.objects.get(id=visit.id)
        # Compare coordinates with some tolerance if needed, or exact match
        # GeoDjango: x=longitude, y=latitude
        if (
            retrieved_visit.location.x == 31.2357
            and retrieved_visit.location.y == 30.0444
        ):
            print(f"Read Visit: {retrieved_visit.id} - Location Matches")
        else:
            print(
                f"Read Visit: {retrieved_visit.id} - Location MISMATCH: {retrieved_visit.location}"
            )
            return False

        # 5. Delete
        visit_id = visit.id
        visit.delete()

        # Verify deletion
        if not Visit.objects.filter(id=visit_id).exists():
            print(f"Deleted Visit: {visit_id}")
        else:
            print("FAILED: Visit was not deleted.")
            return False

        return True

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"CRUD Verification FAILED: {e}")
        return False
    finally:
        # Cleanup user
        if user:
            try:
                user.delete()
                print("Cleanup: User deleted.")
            except Exception as e:
                print(f"Cleanup Failed: {e}")


if __name__ == "__main__":
    print("-" * 30)
    print("Running Local DB Verification")
    print("-" * 30)

    postgis_ok = verify_postgis()
    crud_ok = verify_crud()

    if postgis_ok and crud_ok:
        print("-" * 30)
        print("SUCCESS: Database verification passed.")
        sys.exit(0)
    else:
        print("-" * 30)
        print("FAILURE: Database verification failed.")
        sys.exit(1)
