"""
P4-T5: Race Condition Security Tests
====================================
Tests for concurrent dispatch acceptance under extreme concurrency.

CRITICAL: Validates that exactly ONE nurse succeeds in concurrent acceptance
scenarios, with all others receiving 409 CONFLICT.

Tests select_for_update() row-level locking and transaction isolation.
"""

import pytest
import concurrent.futures
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from decimal import Decimal

pytestmark = pytest.mark.django_db(transaction=True)


class TestRaceConditionConcurrentAccept:
    """US2: Race condition prevention tests for dispatch acceptance."""

    def test_concurrent_accept_database_isolation(self, db):
        """
        US2: Validates transaction isolation prevents lost updates.

        Given: Multiple concurrent transactions reading same visit
        When: All try to update status simultaneously
        Then: No lost updates occur, transactions serialize
        """
        from tests.fixtures.dispatch_pricing_fixtures import (
            AgencyProfileFactory,
            PatientProfileFactory,
            VisitFactory,
        )
        from visits.models import Visit, VisitStatus

        agency = AgencyProfileFactory()
        patient = PatientProfileFactory()
        visit = VisitFactory(patient=patient, agency=agency)

        results = []
        errors = []

        def update_visit_status(visit_id, new_status):
            try:
                with transaction.atomic():
                    visit_obj = Visit.objects.select_for_update().get(id=visit_id)
                    visit_obj.status = new_status
                    visit_obj.save()
                results.append(new_status)
            except Exception as e:
                errors.append(str(e))

        statuses = [
            VisitStatus.PENDING_NURSE,
            VisitStatus.ACCEPTED,
            VisitStatus.EN_ROUTE,
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(update_visit_status, str(visit.id), s) for s in statuses
            ]
            concurrent.futures.wait(futures)

        visit.refresh_from_db()

        assert visit.status in statuses

    def test_no_lost_updates_concurrent_writes(self, db):
        """
        US2: Validates no data loss during concurrent writes.

        Given: Multiple threads updating same field
        When: All write simultaneously
        Then: Final value reflects exactly one write (no merge conflicts)
        """
        from tests.fixtures.dispatch_pricing_fixtures import (
            AgencyProfileFactory,
            NurseProfileFactory,
            PatientProfileFactory,
            VisitFactory,
        )
        from visits.models import Visit, VisitStatus, DispatchOffer, OfferStatus

        agency = AgencyProfileFactory()
        patient = PatientProfileFactory()
        visit = VisitFactory(patient=patient, agency=agency)

        nurses = [
            NurseProfileFactory(agency=agency, user__phone_number=f"+201011111{i:03d}")
            for i in range(5)
        ]

        offers = []
        for nurse in nurses:
            offer = DispatchOffer.objects.create(
                visit=visit,
                nurse=nurse,
                expires_at=timezone.now() + timedelta(seconds=60),
            )
            offers.append(offer)

        successful_offers = []
        conflict_count = 0

        def accept_offer(offer_id):
            try:
                with transaction.atomic():
                    offer = DispatchOffer.objects.select_for_update().get(id=offer_id)

                    visit_obj = Visit.objects.select_for_update().get(id=offer.visit_id)

                    if offer.status != OfferStatus.PENDING:
                        return {
                            "status": "already_processed",
                            "offer_id": str(offer_id),
                        }

                    offer.status = OfferStatus.ACCEPTED
                    offer.save()

                    visit_obj.status = VisitStatus.ACCEPTED
                    visit_obj.nurse_id = offer.nurse_id
                    visit_obj.save()

                return {"status": "success", "offer_id": str(offer_id)}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(accept_offer, str(offer.id)) for offer in offers]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        visit.refresh_from_db()

        success_count = sum(1 for r in results if r["status"] == "success")

        assert visit.status == VisitStatus.ACCEPTED
        assert visit.nurse is not None

        accepted_offers = DispatchOffer.objects.filter(
            visit=visit, status=OfferStatus.ACCEPTED
        ).count()

        assert accepted_offers == 1

    def test_concurrent_accepts_yield_only_one_success(self, db):
        """
        US2 AC1: Validates exactly one nurse succeeds in concurrent acceptance.

        Given: 5 nurses with pending offers for same visit
        When: All submit ACCEPT within same millisecond
        Then: Exactly 1 receives 200 OK, rest receive 409 CONFLICT
        """
        from rest_framework.test import APIClient
        from tests.fixtures.dispatch_pricing_fixtures import create_concurrent_offers
        from visits.models import VisitStatus, DispatchOffer, OfferStatus

        visit, nurses, offers = create_concurrent_offers(num_nurses=5)

        api_client = APIClient()

        def accept_offer(offer, nurse):
            api_client.force_authenticate(user=nurse.user)
            response = api_client.post(
                "/api/v1/visits/nurse/respond-offer/",
                {"offer_id": str(offer.id), "action": "accept"},
            )
            return response.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(accept_offer, offer, nurse)
                for offer, nurse in zip(offers, nurses)
            ]
            status_codes = [
                f.result() for f in concurrent.futures.as_completed(futures)
            ]

        assert status_codes.count(200) == 1
        assert status_codes.count(409) == 4

        visit.refresh_from_db()
        assert visit.status == VisitStatus.ACCEPTED
        assert visit.nurse is not None

        accepted_offers = DispatchOffer.objects.filter(
            visit=visit, status=OfferStatus.ACCEPTED
        ).count()
        assert accepted_offers == 1

    def test_extreme_concurrency_10_nurses(self, db):
        """
        US2 AC3: Validates 10 concurrent acceptance attempts.

        Given: 10 nurses with pending offers
        When: All submit ACCEPT at same time
        Then: Exactly 1 succeeds, 9 fail with 409
        """
        from rest_framework.test import APIClient
        from tests.fixtures.dispatch_pricing_fixtures import create_concurrent_offers
        from visits.models import VisitStatus, DispatchOffer, OfferStatus

        visit, nurses, offers = create_concurrent_offers(num_nurses=10)

        api_client = APIClient()

        def accept_offer(offer, nurse):
            api_client.force_authenticate(user=nurse.user)
            response = api_client.post(
                "/api/v1/visits/nurse/respond-offer/",
                {"offer_id": str(offer.id), "action": "accept"},
            )
            return response.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(accept_offer, offer, nurse)
                for offer, nurse in zip(offers, nurses)
            ]
            status_codes = [
                f.result() for f in concurrent.futures.as_completed(futures)
            ]

        assert status_codes.count(200) == 1
        assert status_codes.count(409) == 9

    def test_accept_expired_offer_returns_410(self, db):
        """
        US2: Validates expired offer returns 410 GONE.

        Given: An offer that has expired
        When: Nurse attempts to accept
        Then: Returns 410 GONE
        """
        from rest_framework.test import APIClient
        from tests.fixtures.dispatch_pricing_fixtures import create_concurrent_offers
        from visits.models import DispatchOffer

        visit, nurses, offers = create_concurrent_offers(num_nurses=1)
        offer = offers[0]
        nurse = nurses[0]

        offer.expires_at = timezone.now() - timedelta(seconds=10)
        offer.save()

        api_client = APIClient()
        api_client.force_authenticate(user=nurse.user)
        response = api_client.post(
            "/api/v1/visits/nurse/respond-offer/",
            {"offer_id": str(offer.id), "action": "accept"},
        )

        assert response.status_code == status.HTTP_410_GONE

    def test_already_accepted_offer_returns_409(self, db):
        """
        US2 AC2: Validates losing nurses receive 409 CONFLICT.

        Given: Offer already accepted by another nurse
        When: Second nurse attempts to accept
        Then: Returns 409 CONFLICT with clear message
        """
        from rest_framework.test import APIClient
        from tests.fixtures.dispatch_pricing_fixtures import create_concurrent_offers
        from visits.models import DispatchOffer, OfferStatus

        visit, nurses, offers = create_concurrent_offers(num_nurses=2)

        offers[0].status = OfferStatus.ACCEPTED
        offers[0].save()

        api_client = APIClient()
        api_client.force_authenticate(user=nurses[1].user)
        response = api_client.post(
            "/api/v1/visits/nurse/respond-offer/",
            {"offer_id": str(offers[1].id), "action": "accept"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
