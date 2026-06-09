from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point, Polygon

from users.models import (
    AgencyProfile,
    AgencyStatus,
    CustomUser,
    DispatchMode,
)
from visits.models import Visit, VisitStatus
from visits.tasks import re_route_visit


@pytest.mark.django_db
class TestCeleryRerouteLogic:
    """Verification for re_route_visit prevents infinite loops and follows agency rank."""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Create a patient
        u = CustomUser.objects.create(national_id="12345678901234", phone_number="+201000000001", role="PATIENT")
        from users.models import PatientProfile
        self.patient = PatientProfile.objects.create(user=u)

        # Create 3 agencies covering the same area
        self.loc = Point(31.2357, 30.0444, srid=4326)

        self.agencies = []
        for i in range(3):
            ua = CustomUser.objects.create(national_id=f"1111111111111{i}", phone_number=f"+2010000000{i+2}", role="AGENCY_ADMIN")
            ag = AgencyProfile.objects.create(
                user=ua,
                agency_name=f"Agency {i}",
                status=AgencyStatus.VERIFIED,
                is_active=True,
                coverage_polygon=Polygon(
                ((31.0, 30.0), (31.5, 30.0), (31.5, 30.5), (31.0, 30.5), (31.0, 30.0)),
                srid=4326
            ),
                dispatch_mode=DispatchMode.MANUAL
            )
            self.agencies.append(ag)

        # Create visit assigned to Agency 0
        self.visit = Visit.objects.create(
            patient=self.patient,
            status=VisitStatus.PENDING_AGENCY,
            location=self.loc,
            agency=self.agencies[0],
            base_price=Decimal("100.00"),
            final_price=Decimal("100.00")
        )

    def test_reroute_exhaustion_cancels_visit(self):
        """Verify that after trying all agencies, the visit is cancelled."""
        # Agency 0 is already tried.
        # Attempt 1: Reroute from Agency 0
        re_route_visit(str(self.visit.id), str(self.agencies[0].id))
        self.visit.refresh_from_db()
        assert self.visit.agency_id != self.agencies[0].id
        assert self.visit.status == VisitStatus.PENDING_AGENCY

        current_ag_id = self.visit.agency_id

        # Attempt 2: Reroute from currently assigned agency
        re_route_visit(str(self.visit.id), str(current_ag_id))
        self.visit.refresh_from_db()

        # Final attempt: Reroute from the last one
        last_ag_id = self.visit.agency_id
        re_route_visit(str(self.visit.id), str(last_ag_id))

        self.visit.refresh_from_db()
        # Should be cancelled now as no more agencies cover the area that haven't been tried
        assert self.visit.status == VisitStatus.CANCELLED
        assert self.visit.agency is None
