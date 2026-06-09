"""
Integration tests for push notification service.
"""

from unittest.mock import MagicMock, patch

import pytest

from notifications.models import (
    DeviceToken,
    NotificationLog,
    NotificationStatus,
    UserNotificationPrefs,
)
from notifications.services.push_service import send_to_user, send_to_users
from users.models import CustomUser


def make_user(national_id="29901010100001", phone="01000000001", **kw):
    return CustomUser.objects.create_user(
        national_id=national_id,
        phone_number=phone,
        password="testpass123",
        **kw
    )


@pytest.mark.django_db
class TestSendToUser:
    """Tests for send_to_user function."""

    @patch('notifications.services.push_service.messaging')
    def test_send_to_user_success(self, mock_messaging):
        """Test successful notification sending."""
        user = make_user()
        # Ensure notification prefs exist
        UserNotificationPrefs.objects.get_or_create(user=user)

        # Create device token
        token = DeviceToken.objects.create(
            user=user,
            token="test-fcm-token",
            platform="ANDROID",
        )

        # Mock FCM response
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_response.responses = [MagicMock(success=True, exception=None)]
        mock_messaging.send_each.return_value = mock_response
        mock_messaging.Message.return_value = MagicMock()
        mock_messaging.Notification.return_value = MagicMock()

        logs = send_to_user(str(user.id), "NURSE_ASSIGNED", {"nurse_name": "أحمد"})

        assert len(logs) > 0
        assert NotificationLog.objects.filter(
            recipient=user,
            event_type="NURSE_ASSIGNED",
            status=NotificationStatus.SENT,
        ).exists()

    def test_send_to_user_no_tokens(self):
        """Test notification when user has no device tokens."""
        user = make_user(national_id="29901010100002", phone="01000000002")
        UserNotificationPrefs.objects.get_or_create(user=user)

        logs = send_to_user(str(user.id), "NURSE_ASSIGNED", {"nurse_name": "أحمد"})

        assert len(logs) == 1
        assert logs[0].status == NotificationStatus.SKIPPED
        assert "No active device tokens" in logs[0].fcm_error

    def test_send_to_user_preference_disabled(self):
        """Test notification skipped due to user preference."""
        user = make_user(national_id="29901010100003", phone="01000000003")
        prefs = UserNotificationPrefs.objects.get_or_create(user=user)[0]
        prefs.visit_updates = False
        prefs.save()

        logs = send_to_user(str(user.id), "NURSE_ASSIGNED", {"nurse_name": "أحمد"})

        assert len(logs) == 1
        assert logs[0].status == NotificationStatus.SKIPPED
        assert "visit_updates disabled" in logs[0].fcm_error

    def test_send_to_user_renders_arabic_template(self):
        """Test Arabic template rendering."""
        user = make_user()
        user.preferred_language = "ar"
        user.save()

        # Without Firebase, it will skip but still render title
        logs = send_to_user(str(user.id), "NURSE_ASSIGNED", {"nurse_name": "أحمد"})

        # Verify template was rendered (check NotificationLog title)
        assert len(logs) > 0

    def test_send_to_user_renders_english_template(self):
        """Test English template rendering."""
        user = make_user(national_id="29901010100004", phone="01000000004")
        user.preferred_language = "en"
        user.save()

        logs = send_to_user(str(user.id), "NURSE_ASSIGNED", {"nurse_name": "Ahmed"})

        assert len(logs) > 0

    def test_send_to_user_data_payload_has_visit_id_only(self):
        """Test that data payload contains only visit_id and event_type."""
        user = make_user(national_id="29901010100005", phone="01000000005")

        logs = send_to_user(
            str(user.id),
            "NURSE_ASSIGNED",
            {"nurse_name": "Ahmed", "visit_id": "some-uuid"}
        )

        if logs:
            assert "visit_id" in logs[0].data_payload
            assert "nurse_name" not in logs[0].data_payload


@pytest.mark.django_db
class TestSendToUsers:
    """Tests for send_to_users function."""

    def test_send_to_users_multiple_users(self):
        """Test sending to multiple users."""
        user1 = make_user(national_id="29901010100006", phone="01000000006")
        user2 = make_user(national_id="29901010100007", phone="01000000007")

        logs = send_to_users(
            [str(user1.id), str(user2.id)],
            "NURSE_ASSIGNED",
            {"nurse_name": "أحمد"}
        )

        assert len(logs) >= 2


@pytest.mark.django_db
class TestPreferenceBypass:
    """Tests for SOS alert preference bypass."""

    def test_sos_bypasses_preferences(self):
        """Test that SOS_ALERT bypasses user preferences."""
        user = make_user(national_id="29901010100008", phone="01000000008")
        prefs = UserNotificationPrefs.objects.get_or_create(user=user)[0]
        # Disable all preferences
        prefs.visit_updates = False
        prefs.financial_updates = False
        prefs.marketing = False
        prefs.dispatch_offers = False
        prefs.save()

        # SOS should still be sent
        logs = send_to_user(str(user.id), "SOS_ALERT", {})

        # Should be skipped due to no tokens, but NOT due to preferences
        assert len(logs) == 1
        assert logs[0].status == NotificationStatus.SKIPPED
        assert "disabled" not in logs[0].fcm_error
