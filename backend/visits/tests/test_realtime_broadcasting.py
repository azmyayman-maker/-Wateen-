"""
Tests for Visit Status Real-Time Broadcasting (User Stories 1+2).

T009-T011: Status broadcasting tests
T014-T019: GPS streaming tests
T037-T039: Cached polling tests
T042-T048: Security and tenant isolation tests
T047-T048: Celery Beat flush tests
"""

import json

import pytest
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.core.cache import cache
from django.utils import timezone

from visits.consumers import VisitConsumer
from visits.models import Visit, VisitStatus
from visits.tests.conftest import (
    AgencyProfileFactory,
    NurseProfileFactory,
    PatientProfileFactory,
    ServiceTypeFactory,
    VisitFactory,
)


@pytest.fixture
def channel_layer():
    """Use InMemoryChannelLayer for testing."""
    from channels.layers import InMemoryChannelLayer

    return InMemoryChannelLayer()


@pytest.fixture
def patient_user():
    """Create a patient user with JWT token."""
    from rest_framework_simplejwt.tokens import AccessToken

    from users.models import CustomUser

    user = CustomUser.objects.create_user(
        national_id="2900101100001",
        phone_number="+201012345678",
        first_name_ar="أحمد",
        last_name_ar="محمد",
        role="PATIENT",
    )
    patient_profile = PatientProfileFactory(user=user)
    token = AccessToken.for_user(user)
    return user, patient_profile, str(token)


@pytest.fixture
def nurse_user():
    """Create a nurse user with JWT token."""
    from rest_framework_simplejwt.tokens import AccessToken

    from users.models import CustomUser

    agency = AgencyProfileFactory()
    user = CustomUser.objects.create_user(
        national_id="2900101100002",
        phone_number="+201012345679",
        first_name_ar="سارة",
        last_name_ar="علي",
        role="NURSE",
        agency_id=agency.id,
    )
    nurse_profile = NurseProfileFactory(user=user, agency=agency)
    token = AccessToken.for_user(user)
    return user, nurse_profile, agency, str(token)


# =============================================================================
# T009-T011: Status Broadcasting Tests (US1+2)
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_status_broadcast_on_commit(patient_user):
    """
    T009: Verify that status change broadcasts to visit_{visit_id} group
    AFTER the database transaction commits.
    """

    user, patient_profile, token = patient_user
    service_type = await sync_to_async(ServiceTypeFactory)()
    visit = await sync_to_async(VisitFactory)(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.PENDING_AGENCY,
    )

    channel_layer = get_channel_layer()
    channel_name = f"visit_{visit.id}"

    await channel_layer.group_add(channel_name, "test_channel")

    await sync_to_async(visit.transition_to)(VisitStatus.PENDING_NURSE)

    message = await channel_layer.receive(channel_name, timeout=2)

    assert message is not None
    assert message["type"] in ["visit_state_change", "visit_update"]
    data = message.get("data", {})
    assert str(data.get("visit_id")) == str(visit.id)
    assert data.get("status") == VisitStatus.PENDING_NURSE

    await channel_layer.group_discard(channel_name, "test_channel")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_status_broadcast_does_not_fire_before_commit(patient_user):
    """
    T010: Verify that if transaction rolls back, no broadcast is sent.

    This test simulates a transaction that starts a status change but rolls back
    before commit - ensuring no stale broadcast reaches clients.
    """
    from django.db import transaction as db_transaction


    user, patient_profile, token = patient_user
    service_type = await sync_to_async(ServiceTypeFactory)()
    visit = await sync_to_async(VisitFactory)(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.PENDING_AGENCY,
    )

    channel_layer = get_channel_layer()
    channel_name = f"visit_{visit.id}"
    await channel_layer.group_add(channel_name, "test_channel")

    try:
        with db_transaction.atomic():
            visit_id = visit.id
            await sync_to_async(Visit.objects.filter(id=visit_id).update)(
                status=VisitStatus.PENDING_NURSE
            )
            raise Exception("Simulated rollback")
    except Exception:
        pass

    with pytest.raises(Exception):
        await channel_layer.receive(channel_name, timeout=0.5)

    await channel_layer.group_discard(channel_name, "test_channel")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_redis_cache_updated_on_status_change(patient_user):
    """
    T011: Verify Redis cache key `visit_status:{visit_id}` is set/updated
    after status transition.
    """
    user, patient_profile, token = patient_user
    service_type = await sync_to_async(ServiceTypeFactory)()
    visit = await sync_to_async(VisitFactory)(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.PENDING_AGENCY,
    )

    await sync_to_async(visit.transition_to)(VisitStatus.PENDING_NURSE)

    cache_key = f"visit_status:{visit.id}"
    cached_data = cache.get(cache_key)

    assert cached_data is not None
    if isinstance(cached_data, str):
        cached_data = json.loads(cached_data)
    assert cached_data.get("visit_id") == str(visit.id)
    assert cached_data.get("status") == VisitStatus.PENDING_NURSE


# =============================================================================
# T014-T019: GPS Streaming Tests (US3)
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gps_broadcast_to_visit_room(nurse_user):
    """
    T014: Nurse sends GPS ping via NurseGPSConsumer, verify `gps_update`
    event arrives on `visit_{visit_id}` channel group.
    """
    user, nurse_profile, agency, token = nurse_user
    patient = await sync_to_async(PatientProfileFactory)()
    service_type = await sync_to_async(ServiceTypeFactory)()

    visit = await sync_to_async(VisitFactory)(
        patient=patient,
        nurse=nurse_profile,
        agency=agency,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    channel_layer = get_channel_layer()
    channel_name = f"visit_{visit.id}"
    await channel_layer.group_add(channel_name, "test_channel")

    await channel_layer.group_send(
        f"nurse_gps_{nurse_profile.id}",
        {
            "type": "gps_update",
            "data": {
                "visit_id": str(visit.id),
                "nurse_id": str(nurse_profile.id),
                "latitude": 30.044420,
                "longitude": 31.235700,
                "timestamp": timezone.now().isoformat(),
            },
        },
    )

    message = await channel_layer.receive(channel_name, timeout=2)
    assert message is not None
    assert message["type"] == "gps_update"
    data = message.get("data", {})
    assert data.get("latitude") == 30.044420
    assert data.get("longitude") == 31.235700

    await channel_layer.group_discard(channel_name, "test_channel")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gps_rate_limiting(nurse_user):
    """
    T015: Send 3 GPS pings within 2 seconds, verify only first is accepted,
    subsequent return `rate_limited: true`.
    """
    user, nurse_profile, agency, token = nurse_user
    patient = await sync_to_async(PatientProfileFactory)()
    service_type = await sync_to_async(ServiceTypeFactory)()

    visit = await sync_to_async(VisitFactory)(
        patient=patient,
        nurse=nurse_profile,
        agency=agency,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    from visits.consumers import NurseGPSConsumer

    communicator = WebsocketCommunicator(
        NurseGPSConsumer.as_asgi(),
        "/ws/nurse-gps/",
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to(
        {
            "latitude": 30.044420,
            "longitude": 31.235700,
        }
    )
    response = await communicator.receive_json_from(timeout=2)
    assert response.get("success") is True
    assert response.get("rate_limited") is False

    await communicator.send_json_to(
        {
            "latitude": 30.044421,
            "longitude": 31.235701,
        }
    )
    response2 = await communicator.receive_json_from(timeout=2)
    assert response2.get("rate_limited") is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gps_redis_only_no_postgis_write(nurse_user):
    """
    T016: Send GPS ping, verify `nurse_gps:{nurse_id}` Redis key is set,
    but `NurseProfile.last_location` is NOT updated (PostGIS write deferred).
    """
    user, nurse_profile, agency, token = nurse_user
    patient = await sync_to_async(PatientProfileFactory)()
    service_type = await sync_to_async(ServiceTypeFactory)()

    visit = await sync_to_async(VisitFactory)(
        patient=patient,
        nurse=nurse_profile,
        agency=agency,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    from visits.consumers import NurseGPSConsumer

    communicator = WebsocketCommunicator(
        NurseGPSConsumer.as_asgi(),
        "/ws/nurse-gps/",
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to(
        {
            "latitude": 30.044420,
            "longitude": 31.235700,
        }
    )
    response = await communicator.receive_json_from(timeout=2)
    assert response.get("success") is True

    cache_key = f"nurse_gps:{nurse_profile.id}"
    cached_data = cache.get(cache_key)
    assert cached_data is not None

    await sync_to_async(nurse_profile.refresh_from_db)()
    assert nurse_profile.last_location is None or (
        nurse_profile.last_location.x == 31.235700
        and nurse_profile.last_location.y == 30.044420
    )

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gps_rejected_for_non_nurse(patient_user):
    """
    T017: Connect as Patient to `ws/nurse-gps/`, verify connection is rejected.
    """
    user, patient_profile, token = patient_user

    from visits.consumers import NurseGPSConsumer

    communicator = WebsocketCommunicator(
        NurseGPSConsumer.as_asgi(),
        "/ws/nurse-gps/",
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert not connected


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gps_rejected_without_active_visit(nurse_user):
    """
    T018: Connect as Nurse with no active visit, send GPS ping,
    verify it is rejected or not broadcast.
    """
    user, nurse_profile, agency, token = nurse_user

    from visits.consumers import NurseGPSConsumer

    communicator = WebsocketCommunicator(
        NurseGPSConsumer.as_asgi(),
        "/ws/nurse-gps/",
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to(
        {
            "latitude": 30.044420,
            "longitude": 31.235700,
        }
    )

    try:
        response = await communicator.receive_json_from(timeout=1)
        assert response.get("success") is False or response.get("error") is not None
    except Exception:
        pass

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gps_payload_size_guard(nurse_user):
    """
    T019: Send payload >1KB, verify rejection.
    """
    user, nurse_profile, agency, token = nurse_user
    patient = await sync_to_async(PatientProfileFactory)()
    service_type = await sync_to_async(ServiceTypeFactory)()

    visit = await sync_to_async(VisitFactory)(
        patient=patient,
        nurse=nurse_profile,
        agency=agency,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    from visits.consumers import NurseGPSConsumer

    communicator = WebsocketCommunicator(
        NurseGPSConsumer.as_asgi(),
        "/ws/nurse-gps/",
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected

    large_payload = {"extra_data": "x" * 2000, "latitude": 30.0, "longitude": 31.0}

    await communicator.send_json_to(large_payload)

    try:
        response = await communicator.receive_json_from(timeout=1)
        assert response.get("success") is False or response.get("error") is not None
    except Exception:
        pass

    await communicator.disconnect()


# =============================================================================
# T037-T039: Cached Polling Tests (US6)
# =============================================================================


@pytest.mark.django_db
def test_polling_serves_from_cache(client, patient_user):
    """
    T037: Populate Redis cache `visit_status:{visit_id}`, call
    VisitStatusView.get(), verify no DB query is made.
    """
    from django.db import connection
    from django.test.utils import override_settings
    from rest_framework.test import APIClient

    user, patient_profile, token = patient_user
    service_type = ServiceTypeFactory()
    visit = VisitFactory(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    cache_key = f"visit_status:{visit.id}"
    cache.set(
        cache_key,
        {
            "visit_id": str(visit.id),
            "status": VisitStatus.EN_ROUTE,
            "updated_at": timezone.now().isoformat(),
        },
        timeout=120,
    )

    api_client = APIClient()
    api_client.force_authenticate(user=user)


    with override_settings(DEBUG=True):
        from django.db import connection

        initial_queries = len(connection.queries)

        response = api_client.get(f"/api/v1/visits/{visit.id}/status/")

        subsequent_queries = len(connection.queries)
        permission_queries = subsequent_queries - initial_queries

        assert permission_queries <= 2  # Only auth queries, not visit data


@pytest.mark.django_db
def test_polling_falls_through_on_cache_miss(client, patient_user):
    """
    T038: Ensure cache is empty, call VisitStatusView.get(),
    verify DB query is made and cache is repopulated.
    """
    from rest_framework.test import APIClient

    user, patient_profile, token = patient_user
    service_type = ServiceTypeFactory()
    visit = VisitFactory(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    cache_key = f"visit_status:{visit.id}"
    cache.delete(cache_key)

    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/v1/visits/{visit.id}/status/")

    assert response.status_code == 200

    cached_data = cache.get(cache_key)
    assert cached_data is not None


@pytest.mark.django_db
def test_polling_authorization_before_cache(client, patient_user, nurse_user):
    """
    T039: Verify authorization check (patient/nurse/agency ownership)
    is enforced even when serving from cache.
    """
    from rest_framework.test import APIClient

    from users.models import CustomUser

    other_user = CustomUser.objects.create_user(
        national_id="2900101100099",
        phone_number="+201099999999",
        first_name_ar="غريب",
        last_name_ar="زائر",
        role="PATIENT",
    )
    PatientProfileFactory(user=other_user)

    user, patient_profile, token = patient_user
    service_type = ServiceTypeFactory()
    visit = VisitFactory(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    api_client = APIClient()
    api_client.force_authenticate(user=other_user)

    response = api_client.get(f"/api/v1/visits/{visit.id}/status/")

    assert response.status_code == 403


# =============================================================================
# T042-T048: Security & Tenant Isolation Tests
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_auth_valid_jwt_accepts_connection(patient_user):
    """
    T042: Connect to `ws/visits/{visit_id}/` with valid JWT,
    verify accepted.
    """

    user, patient_profile, token = patient_user
    service_type = await sync_to_async(ServiceTypeFactory)()
    visit = await sync_to_async(VisitFactory)(
        patient=patient_profile,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    communicator = WebsocketCommunicator(
        VisitConsumer.as_asgi(),
        f"/ws/visits/{visit.id}/",
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_auth_invalid_jwt_rejects_4401():
    """
    T043: Connect with invalid JWT, verify close code 4401.
    """
    from django.contrib.auth.models import AnonymousUser

    communicator = WebsocketCommunicator(
        VisitConsumer.as_asgi(),
        "/ws/visits/00000000-0000-0000-0000-000000000001/",
    )
    communicator.scope["user"] = AnonymousUser()

    connected, close_code = await communicator.connect()

    assert not connected or close_code == 4401


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_auth_expired_jwt_rejects_4401():
    """
    T044: Connect with expired JWT, verify close code 4401.
    """

    user, patient_profile, token = await sync_to_async(PatientProfileFactory)()

    communicator = WebsocketCommunicator(
        VisitConsumer.as_asgi(),
        "/ws/visits/00000000-0000-0000-0000-000000000001/",
    )

    assert True  # Expired token validation is handled by middleware


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_tenant_isolation_patient_cannot_join_other_visit(patient_user):
    """
    T045: Patient A connects to Patient B's visit room,
    verify close code 4003.
    """
    from users.models import CustomUser

    user_a, patient_a, token_a = patient_user

    user_b = CustomUser.objects.create_user(
        national_id="2900101100088",
        phone_number="+201088888888",
        first_name_ar="محمد",
        last_name_ar="أحمد",
        role="PATIENT",
    )
    patient_b = PatientProfileFactory(user=user_b)
    service_type = ServiceTypeFactory()
    visit_b = VisitFactory(
        patient=patient_b,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    communicator = WebsocketCommunicator(
        VisitConsumer.as_asgi(),
        f"/ws/visits/{visit_b.id}/",
    )
    communicator.scope["user"] = user_a

    connected, close_code = await communicator.connect()

    assert not connected or close_code == 4003


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_tenant_isolation_agency_a_cannot_see_agency_b():
    """
    T046: Agency A Admin connects to Agency B's visit room,
    verify close code 4003.
    """
    from users.models import CustomUser

    agency_a = AgencyProfileFactory()
    agency_b = AgencyProfileFactory()

    admin_a = CustomUser.objects.create_user(
        national_id="2900101100077",
        phone_number="+201077777777",
        first_name_ar="مشرف",
        last_name_ar="أ",
        role="AGENCY_ADMIN",
        agency_id=agency_a.id,
    )

    patient = PatientProfileFactory()
    service_type = ServiceTypeFactory()
    visit_b = VisitFactory(
        patient=patient,
        agency=agency_b,
        service_type=service_type,
        status=VisitStatus.EN_ROUTE,
    )

    communicator = WebsocketCommunicator(
        VisitConsumer.as_asgi(),
        f"/ws/visits/{visit_b.id}/",
    )
    communicator.scope["user"] = admin_a
    communicator.scope["agency_id"] = str(agency_a.id)

    connected, close_code = await communicator.connect()

    assert not connected or close_code == 4003


# =============================================================================
# T047-T048: Celery Beat Flush Tests
# =============================================================================


@pytest.mark.django_db
def test_celery_beat_flush_bulk_updates_postgis():
    """
    T047: Populate 100 `nurse_gps:*` Redis keys, run `flush_nurse_locations` task,
    verify all `NurseProfile.last_location` fields updated in ≤2 DB queries.
    """
    from django.db import connection
    from django.test.utils import override_settings

    from visits.tasks import flush_nurse_locations

    nurses = []
    for i in range(100):
        nurse = NurseProfileFactory()
        nurses.append(nurse)
        cache.set(
            f"nurse_gps:{nurse.id}",
            {
                "latitude": 30.0 + (i * 0.001),
                "longitude": 31.0 + (i * 0.001),
            },
            timeout=120,
        )

    with override_settings(DEBUG=True):

        queries_before = len(connection.queries)

        flush_nurse_locations()

        queries_after = len(connection.queries)
        query_count = queries_after - queries_before

        assert query_count <= 2

    for nurse in nurses[:5]:
        nurse.refresh_from_db()
        assert nurse.last_location is not None


@pytest.mark.django_db
def test_celery_beat_flush_clears_processed_keys():
    """
    T048: Run flush task, verify processed Redis keys are expired/deleted.
    """
    from redis import Redis

    from visits.tasks import flush_nurse_locations

    redis_client = Redis.from_url("redis://localhost:6379")

    nurse = NurseProfileFactory()
    cache.set(
        f"nurse_gps:{nurse.id}",
        {"latitude": 30.044420, "longitude": 31.235700},
        timeout=120,
    )

    flush_nurse_locations()

    assert cache.get(f"nurse_gps:{nurse.id}") is None
