import pytest
import uuid
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser, AgencyProfile, PatientProfile
from config.middleware import JWTAuthMiddleware
from visits.consumers import AgencyDashboardConsumer, VisitConsumer

# Helper to generate JWT token for a user
def get_user_token(user):
    token = AccessToken.for_user(user)
    if getattr(user, "agency_id", None):
        token["agency_id"] = str(user.agency_id)
    return str(token)

@pytest.fixture
def agency_admin_user(db):
    agency = AgencyProfile.objects.create(
        name="Test Agency",
        commercial_register="123456789",
        license_number="LIC-123"
    )
    user = CustomUser.objects.create_user(
        phone_number="+201000000000",
        password="testpassword",
        role="AGENCY_ADMIN",
        agency=agency
    )
    return user, agency

@pytest.fixture
def patient_user(db):
    user = CustomUser.objects.create_user(
        phone_number="+201000000001",
        password="testpassword",
        role="PATIENT"
    )
    patient = PatientProfile.objects.create(user=user)
    return user, patient

# ==============================================================================
# 1. JWTAuthMiddleware Tests (Query String Parsing and Rejection)
# ==============================================================================

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_jwt_auth_middleware_missing_token():
    async def dummy_app(scope, receive, send):
        pass
    
    application = JWTAuthMiddleware(dummy_app)
    communicator = WebsocketCommunicator(application, "/ws/test/")
    connected, subprotocol = await communicator.connect()
    
    assert not connected
    assert communicator.close_code == 4401  # Unauthorized

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_jwt_auth_middleware_invalid_token():
    async def dummy_app(scope, receive, send):
        pass
    
    application = JWTAuthMiddleware(dummy_app)
    communicator = WebsocketCommunicator(application, "/ws/test/?token=invalid.jwt.token")
    connected, subprotocol = await communicator.connect()
    
    assert not connected
    assert communicator.close_code == 4401

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_jwt_auth_middleware_valid_token(agency_admin_user):
    user, agency = agency_admin_user
    token = get_user_token(user)
    
    async def dummy_app(scope, receive, send):
        assert scope["user"].id == user.id
        await send({"type": "websocket.accept"})
        
    application = JWTAuthMiddleware(dummy_app)
    communicator = WebsocketCommunicator(application, f"/ws/test/?token={token}")
    connected, subprotocol = await communicator.connect()
    
    assert connected
    await communicator.disconnect()

# ==============================================================================
# 2. AgencyDashboardConsumer Tests (Tenant Isolation)
# ==============================================================================

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_agency_dashboard_consumer_valid(agency_admin_user):
    user, agency = agency_admin_user
    token = get_user_token(user)
    
    application = JWTAuthMiddleware(URLRouter([
        path("ws/agency/<uuid:agency_id>/dashboard/", AgencyDashboardConsumer.as_asgi()),
    ]))
    
    # User belongs to the agency requested in the URL
    communicator = WebsocketCommunicator(application, f"/ws/agency/{agency.id}/dashboard/?token={token}")
    connected, subprotocol = await communicator.connect()
    
    assert connected
    await communicator.disconnect()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_agency_dashboard_consumer_cross_tenant_rejection(agency_admin_user):
    user, agency = agency_admin_user
    token = get_user_token(user)
    other_agency_id = uuid.uuid4()
    
    application = JWTAuthMiddleware(URLRouter([
        path("ws/agency/<uuid:agency_id>/dashboard/", AgencyDashboardConsumer.as_asgi()),
    ]))
    
    # User belongs to agency A, but attempts to connect to agency B
    communicator = WebsocketCommunicator(application, f"/ws/agency/{other_agency_id}/dashboard/?token={token}")
    connected, subprotocol = await communicator.connect()
    
    assert not connected
    assert communicator.close_code == 4003  # Forbidden

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_agency_dashboard_consumer_patient_rejection(patient_user, agency_admin_user):
    p_user, patient = patient_user
    _, agency = agency_admin_user
    token = get_user_token(p_user)
    
    application = JWTAuthMiddleware(URLRouter([
        path("ws/agency/<uuid:agency_id>/dashboard/", AgencyDashboardConsumer.as_asgi()),
    ]))
    
    # Patient attempting to access B2B dashboard
    communicator = WebsocketCommunicator(application, f"/ws/agency/{agency.id}/dashboard/?token={token}")
    connected, subprotocol = await communicator.connect()
    
    assert not connected
    assert communicator.close_code == 4003  # Forbidden
