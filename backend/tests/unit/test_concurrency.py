import concurrent.futures
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from visits.models import DispatchOffer, OfferStatus, VisitStatus


@pytest.mark.django_db(transaction=True)
class TestConcurrencyUS2:

    @pytest.fixture
    def setup_offers(self, client):
        from visits.tests.conftest import (
            AgencyProfileFactory,
            NurseProfileFactory,
            PatientProfileFactory,
            VisitFactory,
        )
        agency = AgencyProfileFactory()
        patient = PatientProfileFactory()
        visit = VisitFactory(patient=patient, agency=agency, status=VisitStatus.PENDING_AGENCY)

        nurses = [NurseProfileFactory(user__phone_number=f"+2010111111{i}", agency=agency) for i in range(5)]

        offers = []
        for n in nurses:
            o = DispatchOffer.objects.create(
                visit=visit,
                nurse=n,
                expires_at=timezone.now() + timedelta(seconds=60)
            )
            offers.append(o)

        return visit, nurses, offers

    def test_concurrent_accepts_yield_only_one_success(self, client, setup_offers):
        visit, nurses, offers = setup_offers

        def accept_offer(offer):
            from rest_framework.test import APIClient
            api_client = APIClient()
            api_client.force_authenticate(user=offer.nurse.user)
            return api_client.post('/api/v1/visits/nurse/respond-offer/', {
                "offer_id": str(offer.id),
                "action": "accept"
            })

        # Run 5 requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(accept_offer, o) for o in offers]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        status_codes = [r.status_code for r in responses]

        assert status_codes.count(status.HTTP_200_OK) == 1
        assert status_codes.count(status.HTTP_409_CONFLICT) == 4

        visit.refresh_from_db()
        assert visit.status == VisitStatus.ACCEPTED
        assert visit.nurse is not None

        assert DispatchOffer.objects.filter(visit=visit, status=OfferStatus.ACCEPTED).count() == 1
        assert DispatchOffer.objects.filter(visit=visit, status=OfferStatus.EXPIRED).count() == 4

    def test_accept_expired_offer_returns_410(self, client, setup_offers):
        visit, nurses, offers = setup_offers
        offer = offers[0]
        offer.expires_at = timezone.now() - timedelta(seconds=10)
        offer.save()

        from rest_framework.test import APIClient
        api_client = APIClient()
        api_client.force_authenticate(user=offer.nurse.user)
        response = api_client.post('/api/v1/visits/nurse/respond-offer/', {
            "offer_id": str(offer.id),
            "action": "accept"
        })

        assert response.status_code == status.HTTP_410_GONE

    def test_already_accepted_offer_by_another_nurse(self, client, setup_offers):
        visit, nurses, offers = setup_offers

        # Nurse 1 accepts manually
        offers[0].status = OfferStatus.ACCEPTED
        offers[0].save()
        visit.status = VisitStatus.ACCEPTED
        visit.nurse = nurses[0]
        visit.save()

        # Nurse 2 tries to accept
        from rest_framework.test import APIClient
        api_client = APIClient()
        api_client.force_authenticate(user=nurses[1].user)
        response = api_client.post('/api/v1/visits/nurse/respond-offer/', {
            "offer_id": str(offers[1].id),
            "action": "accept"
        })

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "ممرضة أخرى" in response.data['detail']
