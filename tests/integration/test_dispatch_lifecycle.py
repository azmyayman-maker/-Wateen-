import pytest
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from visits.models import DispatchOffer, OfferStatus, VisitStatus, Visit
from users.models import DispatchMode

@pytest.mark.django_db(transaction=True)
class TestDispatchLifecycleUS4:

    def test_timeout_expiry_and_reroute(self, client):
        from visits.tests.conftest import AgencyProfileFactory, NurseProfileFactory, PatientProfileFactory, VisitFactory
        # T028 & T029
        agency1 = AgencyProfileFactory(manager_name="Agency 1", dispatch_mode=DispatchMode.AUTO)
        agency2 = AgencyProfileFactory(manager_name="Agency 2", dispatch_mode=DispatchMode.AUTO) # For ranking

        patient = PatientProfileFactory()
        from django.contrib.gis.geos import Point
        visit = VisitFactory(patient=patient, agency=agency1, status=VisitStatus.PENDING_AGENCY, location=Point(30.0, 31.0))
        
        nurses = [NurseProfileFactory(user__phone_number=f"+2010111111{i}", agency=agency1) for i in range(5)]
        
        offers = []
        for n in nurses:
            o = DispatchOffer.objects.create(
                visit=visit, nurse=n, expires_at=timezone.now() + timedelta(seconds=60)
            )
            offers.append(o)

        from visits.tasks import check_dispatch_timeout
        # Mocking re_route_visit.delay to call it synchronously for the test
        with patch('visits.tasks.re_route_visit.delay') as mock_reroute:
            mock_reroute.side_effect = lambda v_id, a_id: __import__('visits.tasks').tasks.re_route_visit(v_id, a_id)
            check_dispatch_timeout(str(visit.id))
        
        visit.refresh_from_db()
        
        offers_states = DispatchOffer.objects.filter(visit=visit).values_list('status', flat=True)
        assert all(state == OfferStatus.EXPIRED for state in offers_states)
        
        assert visit.reroute_attempts > 0
        assert visit.agency_id != agency1.id # Rerouted to next or null

    def test_no_agencies_left(self, client):
        from visits.tests.conftest import AgencyProfileFactory, PatientProfileFactory, VisitFactory
        # T030
        agency1 = AgencyProfileFactory(manager_name="Only Agency")
        patient = PatientProfileFactory()
        from django.contrib.gis.geos import Point
        visit = VisitFactory(patient=patient, agency=agency1, status=VisitStatus.PENDING_AGENCY, location=Point(30.0, 31.0))
        
        from visits.tasks import re_route_visit
        re_route_visit(str(visit.id), str(agency1.id))
        
        visit.refresh_from_db()
        assert visit.status == VisitStatus.CANCELLED
        assert visit.agency is None

    def test_idempotency_on_already_accepted(self, client):
        from visits.tests.conftest import AgencyProfileFactory, VisitFactory
        # T031
        agency1 = AgencyProfileFactory()
        visit = VisitFactory(agency=agency1, status=VisitStatus.ACCEPTED)
        
        from visits.tasks import check_dispatch_timeout
        check_dispatch_timeout(str(visit.id))
        
        visit.refresh_from_db()
        assert visit.status == VisitStatus.ACCEPTED
