"""
Database Verification Script

Verifies PostgreSQL/PostGIS connectivity and functionality with structured output.
"""

import os
import sys
import time
import logging
import random

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import connection
from django.contrib.gis.geos import Point

from django.contrib.auth import get_user_model
from visits.models import Visit, VisitStatus
from users.models import PatientProfile, UserRole

from typing import cast
from scripts.verification.base import BaseVerifier
from scripts.verification.config import VerificationConfig, get_config
from scripts.verification.models import (
    DatabaseVerificationResult,
    VerificationStatus,
    CRUDStatus,
)
from scripts.verification.console import print_header, print_database_result


User = get_user_model()


class DatabaseVerifier(BaseVerifier):
    def get_component_name(self) -> str:
        return "database"

    def verify_postgis(self) -> tuple[bool, str | None]:
        with connection.cursor() as cursor:
            cursor.execute("SELECT postgis_version();")
            row = cursor.fetchone()
            if row:
                return True, row[0]
        return False, None

    def verify_crud(self) -> CRUDStatus:
        crud = CRUDStatus()
        user = None
        visit = None

        try:
            national_id = "29001010100003"
            phone = f"010{random.randint(10000000, 99999999)}"

            User.objects.filter(national_id=national_id).delete()
            User.objects.filter(phone_number=phone).delete()

            user = User.objects.create_user(
                national_id=national_id,
                phone_number=phone,
                password="testpassword123",
                role=UserRole.PATIENT,
            )
            crud.create = True
            logger.info("CRUD: User created successfully")

            profile = PatientProfile.objects.get(user=user)

            location = Point(31.2357, 30.0444)
            visit = Visit.objects.create(
                patient=profile, location=location, status=VisitStatus.PENDING_AGENCY
            )
            logger.info(f"CRUD: Visit created with ID {visit.id}")

            retrieved_visit = Visit.objects.get(id=visit.id)
            if (
                retrieved_visit.location.x == 31.2357
                and retrieved_visit.location.y == 30.0444
            ):
                crud.read = True
                logger.info("CRUD: Read verification passed")

            # Update verification
            visit.status = VisitStatus.COMPLETED
            visit.save()
            updated_visit = Visit.objects.get(id=visit.id)
            if updated_visit.status == VisitStatus.COMPLETED:
                crud.update = True
                logger.info("CRUD: Update verification passed")
            
            visit_id = visit.id
            visit.delete()
            # Mark visit as None so finally block doesn't try to delete it again if validation fails later (though here it's last)
            visit = None 

            if not Visit.objects.filter(id=visit_id).exists():
                crud.delete = True
                logger.info("CRUD: Delete verification passed")

        except Exception as e:
            crud.error = str(e)
            logger.error(f"CRUD verification failed: {e}", exc_info=True)
        finally:
            if user:
                try:
                    user.delete()
                    logger.info("CRUD: Cleanup successful")
                except Exception as e:
                    logger.warning(f"CRUD: Cleanup failed: {e}")
        
        return crud

    def verify(self) -> DatabaseVerificationResult:
        latency_ms = 0.0
        postgis_version = None
        crud_status = None
        error = None
        status = VerificationStatus.PASS
        details = []

        try:
            start = time.time()

            postgis_ok, postgis_version = self.verify_postgis()
            latency_ms = (time.time() - start) * 1000

            if not postgis_ok:
                status = VerificationStatus.FAIL
                error = "PostGIS extension not found or not functional"
            else:
                details.append(f"PostGIS {postgis_version}")

                crud_status = self.verify_crud()
                if crud_status.all_passed:
                    details.append("CRUD operations passed")
                else:
                    status = VerificationStatus.FAIL
                    error = "CRUD operations failed"

            if latency_ms > 1000:
                if status == VerificationStatus.PASS:
                    status = VerificationStatus.WARNING
                details.append(f"High latency: {latency_ms:.0f}ms")

        except Exception as e:
            status = VerificationStatus.FAIL
            error = str(e)
            latency_ms = self.elapsed_ms()

        return DatabaseVerificationResult(
            component="database",
            status=status,
            latency_ms=latency_ms,
            postgis_version=postgis_version,
            crud_status=crud_status,
            error=error,
            details=" | ".join(details) if details else "",
        )

    def print_console_output(self) -> None:
        print_header("Database Verification")
        if self.result:
            print_database_result(cast(DatabaseVerificationResult, self.result))


def main() -> int:
    config = get_config()
    verifier = DatabaseVerifier(config)
    return verifier.run()


if __name__ == "__main__":
    sys.exit(main())
