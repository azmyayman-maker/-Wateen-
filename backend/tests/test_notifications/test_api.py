"""
API endpoint tests for notifications.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from notifications.models import DeviceToken
from users.models import CustomUser


def make_user(national_id="29901010100001", phone="01000000001", **kw):
    return CustomUser.objects.create_user(
        national_id=national_id,
        phone_number=phone,
        password="testpass123",
        **kw
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    user = make_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
class TestDeviceTokenAPI:
    def test_register_device_token_success(self, authenticated_client):
        client, user = authenticated_client

        response = client.post(
            '/api/v1/notifications/devices/',
            {"token": "test-fcm-token", "platform": "ANDROID"},
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert DeviceToken.objects.filter(
            user=user,
            token="test-fcm-token",
        ).exists()

    def test_register_device_token_upsert_existing(self, authenticated_client):
        client, user = authenticated_client

        client.post(
            '/api/v1/notifications/devices/',
            {"token": "test-fcm-token", "platform": "ANDROID"},
            format='json',
        )

        response = client.post(
            '/api/v1/notifications/devices/',
            {"token": "test-fcm-token", "platform": "ANDROID"},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK

    def test_register_device_token_invalid_platform(self, authenticated_client):
        client, _ = authenticated_client

        response = client.post(
            '/api/v1/notifications/devices/',
            {"token": "test-fcm-token", "platform": "BLACKBERRY"},
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_device_token_unauthenticated(self, api_client):
        response = api_client.post(
            '/api/v1/notifications/devices/',
            {"token": "test-fcm-token", "platform": "ANDROID"},
            format='json',
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_device_tokens(self, authenticated_client):
        client, user = authenticated_client

        DeviceToken.objects.create(user=user, token="token1", platform="ANDROID", is_active=True)
        DeviceToken.objects.create(user=user, token="token2", platform="IOS", is_active=True)
        DeviceToken.objects.create(user=user, token="token3", platform="WEB", is_active=False)

        response = client.get('/api/v1/notifications/devices/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_delete_device_token_success(self, authenticated_client):
        client, user = authenticated_client

        token = DeviceToken.objects.create(
            user=user,
            token="test-fcm-token",
            platform="ANDROID",
        )

        response = client.delete('/api/v1/notifications/devices/test-fcm-token/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        token.refresh_from_db()
        assert token.is_active is False

    def test_delete_device_token_not_found(self, authenticated_client):
        client, _ = authenticated_client

        response = client.delete('/api/v1/notifications/devices/nonexistent/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_device_token_belongs_to_other_user(self, authenticated_client):
        client, user = authenticated_client

        other_user = make_user(national_id="29901010100002", phone="01000000002")
        DeviceToken.objects.create(
            user=other_user,
            token="other-user-token",
            platform="ANDROID",
        )

        response = client.delete('/api/v1/notifications/devices/other-user-token/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestNotificationPreferencesAPI:
    def test_get_notification_preferences_default(self, authenticated_client):
        client, user = authenticated_client

        response = client.get('/api/v1/notifications/preferences/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data["visit_updates"] is True
        assert response.data["financial_updates"] is True
        assert response.data["marketing"] is True
        assert response.data["dispatch_offers"] is True

    def test_patch_notification_preferences(self, authenticated_client):
        client, user = authenticated_client

        response = client.patch(
            '/api/v1/notifications/preferences/',
            {"financial_updates": False, "marketing": False},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["financial_updates"] is False
        assert response.data["marketing"] is False

    def test_get_preferences_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/notifications/preferences/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_preferences_does_not_expose_sos(self, authenticated_client):
        client, user = authenticated_client

        response = client.get('/api/v1/notifications/preferences/')

        assert "sos" not in response.data
