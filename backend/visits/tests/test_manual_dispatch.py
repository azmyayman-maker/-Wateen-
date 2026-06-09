from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from users.models import UserRole
from visits.models import VisitStatus

# Import factories
from .conftest import AgencyProfileFactory, CustomUserFactory, VisitFactory

pytestmark = pytest.mark.django_db

def test_queue_returns_pending_visits(api_client):
    agency = AgencyProfileFactory(dispatch_mode="MANUAL")
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)

    VisitFactory.create_batch(
        3,
        status=VisitStatus.PENDING_AGENCY,
        agency=agency,
        routed_at=timezone.now()
    )

    api_client.force_authenticate(user=user)
    url = reverse("visits:agency_visit_queue")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3

    visit_data = response.data['results'][0]
    expected_keys = {
        'id', 'patient_district', 'service_type_name',
        'urgency', 'final_price', 'remaining_seconds', 'created_at'
    }
    assert expected_keys.issubset(visit_data.keys())
    assert 295 <= visit_data['remaining_seconds'] <= 300


def test_queue_excludes_other_agencies(api_client):
    agency_a = AgencyProfileFactory(manager_name="Agency A")
    agency_b = AgencyProfileFactory(manager_name="Agency B")
    user_a = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency_a)

    VisitFactory.create_batch(2, status=VisitStatus.PENDING_AGENCY, agency=agency_a, routed_at=timezone.now())
    VisitFactory.create_batch(1, status=VisitStatus.PENDING_AGENCY, agency=agency_b, routed_at=timezone.now())

    api_client.force_authenticate(user=user_a)
    url = reverse("visits:agency_visit_queue")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


def test_queue_countdown_calculation(api_client):
    agency = AgencyProfileFactory()
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)

    # Visit 120s ago => ~180s remaining
    VisitFactory(
        status=VisitStatus.PENDING_AGENCY,
        agency=agency,
        routed_at=timezone.now() - timedelta(seconds=120)
    )

    # Expired visit (310s ago) => should not appear
    VisitFactory(
        status=VisitStatus.PENDING_AGENCY,
        agency=agency,
        routed_at=timezone.now() - timedelta(seconds=310)
    )

    api_client.force_authenticate(user=user)
    url = reverse("visits:agency_visit_queue")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1

    remaining = response.data['results'][0]['remaining_seconds']
    assert 178 <= remaining <= 182


def test_queue_forbidden_for_non_agency_admin(api_client):
    patient_user = CustomUserFactory(role=UserRole.PATIENT)
    nurse_user = CustomUserFactory(role=UserRole.NURSE)

    url = reverse("visits:agency_visit_queue")

    api_client.force_authenticate(user=patient_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(user=nurse_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_queue_empty_for_no_pending(api_client):
    agency = AgencyProfileFactory()
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)

    url = reverse("visits:agency_visit_queue")
    api_client.force_authenticate(user=user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 0

def test_available_nurses_returns_online_only(api_client):
    from .conftest import NurseProfileFactory
    agency = AgencyProfileFactory()
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)

    # Online nurse
    NurseProfileFactory(agency=agency, is_available=True)
    # Offline nurse
    NurseProfileFactory(agency=agency, is_available=False)

    api_client.force_authenticate(user=user)
    url = reverse("visits:agency_available_nurses")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['is_available'] is True

def test_available_nurses_excludes_other_agencies(api_client):
    from .conftest import NurseProfileFactory
    agency_a = AgencyProfileFactory()
    agency_b = AgencyProfileFactory()
    user_a = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency_a)

    NurseProfileFactory(agency=agency_a, is_available=True)
    NurseProfileFactory(agency=agency_b, is_available=True)

    api_client.force_authenticate(user=user_a)
    url = reverse("visits:agency_available_nurses")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

def test_successful_dispatch(api_client):
    from .conftest import NurseProfileFactory
    agency = AgencyProfileFactory(dispatch_mode="MANUAL")
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)
    nurse = NurseProfileFactory(agency=agency, is_available=True)
    visit = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency, routed_at=timezone.now())

    api_client.force_authenticate(user=user)
    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency.id})
    response = api_client.post(url, {"visit_id": visit.id, "nurse_id": nurse.user_id})

    assert response.status_code == status.HTTP_200_OK
    visit.refresh_from_db()
    assert visit.status == VisitStatus.PENDING_NURSE
    assert visit.nurse == nurse
    assert visit.nurse_assigned_at is not None


def test_dispatch_invalid_nurse_from_other_agency(api_client):
    from .conftest import NurseProfileFactory
    agency_a = AgencyProfileFactory()
    agency_b = AgencyProfileFactory()
    user_a = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency_a)
    nurse_b = NurseProfileFactory(agency=agency_b, is_available=True)
    visit_a = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency_a)

    api_client.force_authenticate(user=user_a)
    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency_a.id})
    response = api_client.post(url, {"visit_id": visit_a.id, "nurse_id": nurse_b.user_id})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_dispatch_unavailable_nurse(api_client):
    from .conftest import NurseProfileFactory
    agency = AgencyProfileFactory()
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)
    nurse = NurseProfileFactory(agency=agency, is_available=False)
    visit = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency)

    api_client.force_authenticate(user=user)
    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency.id})
    response = api_client.post(url, {"visit_id": visit.id, "nurse_id": nurse.user_id})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_dispatch_visit_not_pending(api_client):
    from .conftest import NurseProfileFactory
    agency = AgencyProfileFactory()
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)
    nurse = NurseProfileFactory(agency=agency, is_available=True)
    visit = VisitFactory(status=VisitStatus.ACCEPTED, agency=agency)

    api_client.force_authenticate(user=user)
    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency.id})
    response = api_client.post(url, {"visit_id": visit.id, "nurse_id": nurse.user_id})

    assert response.status_code == status.HTTP_409_CONFLICT


def test_dispatch_race_condition(api_client, db):
    import concurrent.futures

    from django.db import connection
    from rest_framework.test import APIClient

    from .conftest import NurseProfileFactory

    agency = AgencyProfileFactory(dispatch_mode="MANUAL")
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)
    nurse1 = NurseProfileFactory(agency=agency, is_available=True)
    nurse2 = NurseProfileFactory(agency=agency, is_available=True)
    visit = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency)

    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency.id})

    def dispatch_nurse(nurse_id):
        connection.close()
        client = APIClient()
        client.force_authenticate(user=user)
        return client.post(url, {"visit_id": visit.id, "nurse_id": nurse_id})

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(dispatch_nurse, nurse1.user_id)
        f2 = executor.submit(dispatch_nurse, nurse2.user_id)
        responses = [f1.result(), f2.result()]

    status_codes = [r.status_code for r in responses]
    assert status.HTTP_200_OK in status_codes
    assert status.HTTP_409_CONFLICT in status_codes or status.HTTP_404_NOT_FOUND in status_codes

    visit.refresh_from_db()
    assert getattr(visit, "nurse", None) is not None

def test_reroute_after_timeout(api_client):
    from django.contrib.gis.geos import Point, Polygon

    from visits.tasks import re_route_visit

    from .conftest import AgencyProfileFactory

    # Create test polygon
    poly = Polygon(((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0)))
    location = Point(5.0, 5.0)

    agency_a = AgencyProfileFactory(dispatch_mode="MANUAL", coverage_polygon=poly)
    agency_b = AgencyProfileFactory(dispatch_mode="MANUAL", coverage_polygon=poly)

    visit = VisitFactory(
        status=VisitStatus.PENDING_AGENCY,
        agency=agency_a,
        location=location,
        routed_at=timezone.now() - timedelta(seconds=301)
    )

    # Run task synchronously
    re_route_visit(str(visit.id), str(agency_a.id))

    visit.refresh_from_db()
    assert visit.agency == agency_b
    assert visit.reroute_attempts == 1
    assert visit.status == VisitStatus.PENDING_AGENCY
    assert visit.routed_at is not None

def test_reroute_idempotent_already_dispatched(api_client):
    from visits.tasks import re_route_visit

    agency = AgencyProfileFactory(dispatch_mode="MANUAL")
    visit = VisitFactory(status=VisitStatus.PENDING_NURSE, agency=agency)

    re_route_visit(str(visit.id), str(agency.id))

    visit.refresh_from_db()
    assert visit.status == VisitStatus.PENDING_NURSE
    assert visit.reroute_attempts == 0

def test_reroute_idempotent_cancelled(api_client):
    from visits.tasks import re_route_visit

    agency = AgencyProfileFactory(dispatch_mode="MANUAL")
    visit = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency)
    visit.transition_to(VisitStatus.CANCELLED)

    re_route_visit(str(visit.id), str(agency.id))

    visit.refresh_from_db()
    assert visit.status == VisitStatus.CANCELLED
    assert visit.reroute_attempts == 0

def test_reroute_no_agencies_cancels(api_client):
    from django.contrib.gis.geos import Point, Polygon

    from visits.tasks import re_route_visit

    from .conftest import AgencyProfileFactory

    poly = Polygon(((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0)))
    location = Point(5.0, 5.0)

    agency_a = AgencyProfileFactory(dispatch_mode="MANUAL", coverage_polygon=poly)

    visit = VisitFactory(
        status=VisitStatus.PENDING_AGENCY,
        agency=agency_a,
        location=location
    )

    re_route_visit(str(visit.id), str(agency_a.id))

    visit.refresh_from_db()
    assert visit.status == VisitStatus.CANCELLED
    assert visit.agency is None

def test_reroute_increments_counter(api_client):
    from django.contrib.gis.geos import Point, Polygon

    from visits.tasks import re_route_visit

    from .conftest import AgencyProfileFactory

    poly = Polygon(((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0)))
    location = Point(5.0, 5.0)

    agency_a = AgencyProfileFactory(dispatch_mode="MANUAL", coverage_polygon=poly)
    agency_b = AgencyProfileFactory(dispatch_mode="MANUAL", coverage_polygon=poly)

    visit = VisitFactory(
        status=VisitStatus.PENDING_AGENCY,
        agency=agency_a,
        location=location,
        reroute_attempts=0
    )

    re_route_visit(str(visit.id), str(agency_a.id))
    visit.refresh_from_db()
    assert visit.reroute_attempts == 1
    assert visit.agency == agency_b

    re_route_visit(str(visit.id), str(agency_b.id))
    visit.refresh_from_db()
    assert visit.reroute_attempts == 2

def test_race_condition_dispatch_vs_timer(api_client, db):
    import concurrent.futures

    from django.db import connection
    from rest_framework.test import APIClient

    from visits.tasks import re_route_visit

    from .conftest import AgencyProfileFactory, NurseProfileFactory

    agency = AgencyProfileFactory(dispatch_mode="MANUAL")
    user = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency)
    nurse = NurseProfileFactory(agency=agency, is_available=True)
    visit = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency)

    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency.id})

    def dispatch_nurse():
        connection.close()
        client = APIClient()
        client.force_authenticate(user=user)
        return client.post(url, {"visit_id": visit.id, "nurse_id": nurse.user_id})

    def run_timer():
        connection.close()
        # Pass a mock celery task so it doesn't fail if we just want to run the code.
        re_route_visit(str(visit.id), str(agency.id))
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(dispatch_nurse)
        f2 = executor.submit(run_timer)
        res1 = f1.result()
        res2 = f2.result()

    visit.refresh_from_db()

    # If dispatch succeeded, it will be 200 and status will be PENDING_NURSE
    if res1.status_code == 200:
        assert visit.status == VisitStatus.PENDING_NURSE
        assert visit.nurse == nurse
    else:
        # If timer succeeded, it will be 409 because the dispatch attempt failed
        assert res1.status_code == 409
        assert visit.status in [VisitStatus.CANCELLED, VisitStatus.PENDING_AGENCY]
        if visit.status == VisitStatus.CANCELLED:
            assert visit.agency is None
        elif visit.status == VisitStatus.PENDING_AGENCY:
            assert visit.agency != agency

def test_cross_agency_dispatch_forbidden(api_client):
    from django.urls import reverse
    from rest_framework import status

    from users.models import UserRole
    from visits.models import VisitStatus

    from .conftest import AgencyProfileFactory, CustomUserFactory, VisitFactory

    agency_a = AgencyProfileFactory(dispatch_mode="MANUAL")
    agency_b = AgencyProfileFactory(dispatch_mode="MANUAL")
    user_a = CustomUserFactory(role=UserRole.AGENCY_ADMIN, agency=agency_a)

    visit_b = VisitFactory(status=VisitStatus.PENDING_AGENCY, agency=agency_b)

    api_client.force_authenticate(user=user_a)
    url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": agency_b.id})
    response = api_client.post(url, {"visit_id": visit_b.id, "nurse_id": "00000000-0000-0000-0000-000000000000"})

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_unauthenticated_access_rejected(api_client):
    import uuid

    from django.urls import reverse
    from rest_framework import status

    # Do NOT authenticate
    url_queue = reverse("visits:agency_visit_queue")
    response_queue = api_client.get(url_queue)
    assert response_queue.status_code == status.HTTP_401_UNAUTHORIZED

    url_nurses = reverse("visits:agency_available_nurses")
    response_nurses = api_client.get(url_nurses)
    assert response_nurses.status_code == status.HTTP_401_UNAUTHORIZED

    url_dispatch = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": str(uuid.uuid4())})
    response_dispatch = api_client.post(url_dispatch, {"visit_id": str(uuid.uuid4()), "nurse_id": str(uuid.uuid4())})
    assert response_dispatch.status_code == status.HTTP_401_UNAUTHORIZED
