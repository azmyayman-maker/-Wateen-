from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError

from users.models import CustomUser, PatientProfile
from visits.models import ServiceType, Visit, VisitStatus


@pytest.mark.django_db
class TestVisitImmutability:
    """Draconian tests ensuring that retroactive modifications to Visit snapshots are technically impossible."""

    def setup_method(self):
        self.user = CustomUser.objects.create(
            national_id="29012011234567",
            phone_number="+201234567891"
        )
        self.patient = PatientProfile.objects.create(user=self.user)
        self.service = ServiceType.objects.create(
            name="General Checkup",
            base_price=Decimal("200.00"),
            expected_duration=30
        )

        # Create an initial Visit representing the atomic request footprint
        self.visit = Visit.objects.create(
            patient=self.patient,
            status=VisitStatus.PENDING_AGENCY,
            location=Point(30.0, 30.0, srid=4326),
            service_type=self.service,
            base_price=Decimal("200.00"),
            distance_fee=Decimal("50.00"),
            distance_km=Decimal("5.00"),
            distance_rate=Decimal("10.00"),
            time_multiplier=Decimal("1.00"),
            ai_surge_coefficient=Decimal("10.00"),
            final_price=Decimal("260.00")
        )

    def test_immutability_lock_prevents_retroactive_price_hike(self):
        db_visit = Visit.objects.get(id=self.visit.id)

        # Attempting to retroactively alter the price
        db_visit.final_price = Decimal("1000.00")

        with pytest.raises(ValidationError) as exc:
            db_visit.save()

        assert exc.value.code == "immutable_pricing"

        # Assert DB untouched
        untouched = Visit.objects.get(id=self.visit.id)
        assert untouched.final_price == Decimal("260.00")

    def test_immutability_lock_allows_status_updates(self):
        db_visit = Visit.objects.get(id=self.visit.id)

        # Agency accepted the visit (Valid transition usually in service layer, but testing ORM here)
        db_visit.status = VisitStatus.PENDING_NURSE
        # Should not raise any validation error regarding pricing
        db_visit.save(update_fields=["status", "updated_at"])

        untouched = Visit.objects.get(id=self.visit.id)
        assert untouched.status == VisitStatus.PENDING_NURSE
        assert untouched.final_price == Decimal("260.00")
