import pytest
from django.contrib.gis.geos import Point

from users.models import VerificationStatus
from visits.models import DispatchOffer
from visits.services.dispatch_service import auto_dispatch_to_nurses


@pytest.mark.django_db
class TestAutoDispatchUS1:

    @pytest.fixture
    def setup_data(self, client):

        from visits.tests.conftest import (
            AgencyProfileFactory,
            NurseProfileFactory,
            PatientProfileFactory,
            VisitFactory,
        )
        agency_a = AgencyProfileFactory(manager_name="Agency A")
        agency_b = AgencyProfileFactory(manager_name="Agency B")

        patient = PatientProfileFactory()
        visit = VisitFactory(patient=patient, agency=agency_a, location=Point(30.0, 31.0))

        # 5 nurses for Agency A at various distances
        nurses_a = []
        for i in range(5):
            np = NurseProfileFactory(user__phone_number=f"+2010000000{i}", agency=agency_a)
            np.is_available = True
            np.verification_status = VerificationStatus.VERIFIED
            np.last_location = Point(30.0 + (i * 0.01), 31.0) # increasingly distant
            np.save()
            nurses_a.append(np)

        # 5 nurses for Agency B at closer distances (Should be ignored!)
        nurses_b = []
        for i in range(5):
            np = NurseProfileFactory(user__phone_number=f"+2010000001{i}", agency=agency_b)
            np.is_available = True
            np.verification_status = VerificationStatus.VERIFIED
            np.last_location = Point(30.0, 31.0) # exactly at patient location
            np.save()
            nurses_b.append(np)

        return visit, agency_a, agency_b, nurses_a, nurses_b

    def test_only_agency_nurses_selected_and_ordered_by_distance(self, setup_data):
        # T010 & T011 test
        visit, agency_a, _, nurses_a, _ = setup_data

        success = auto_dispatch_to_nurses(visit.id, agency_a.id)
        assert success is True

        offers = DispatchOffer.objects.filter(visit=visit).order_by('nurse__last_location')
        assert offers.count() == 5

        # Verify B2B2C enforcement: ALL 5 offers must belong to Agency A
        for offer in offers:
            assert offer.nurse.agency_id == agency_a.id

    def test_unavailable_or_unverified_nurses_ignored(self, setup_data):
        # T012 test with edge cases
        visit, agency_a, _, nurses_a, _ = setup_data

        # Make 2 nurses unavailable, 1 unverified
        nurses_a[0].is_available = False
        nurses_a[0].save()
        nurses_a[1].verification_status = 'PENDING'
        nurses_a[1].save()

        success = auto_dispatch_to_nurses(visit.id, agency_a.id)
        assert success is True

        offers = DispatchOffer.objects.filter(visit=visit)
        assert offers.count() == 3 # Only 3 eligible remaining

    def test_zero_nurses_returns_false(self, setup_data):
        # T013
        visit, agency_a, _, nurses_a, _ = setup_data

        for n in nurses_a:
            n.is_available = False
            n.save()

        success = auto_dispatch_to_nurses(visit.id, agency_a.id)
        assert success is False
        assert DispatchOffer.objects.filter(visit=visit).count() == 0

    def test_null_location_nurse_ignored(self, setup_data):
        # T014
        visit, agency_a, _, nurses_a, _ = setup_data

        nurses_a[0].last_location = None
        nurses_a[0].save()

        success = auto_dispatch_to_nurses(visit.id, agency_a.id)
        assert success is True
        assert DispatchOffer.objects.filter(visit=visit).count() == 4
        assert not DispatchOffer.objects.filter(visit=visit, nurse=nurses_a[0]).exists()
