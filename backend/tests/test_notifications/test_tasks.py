"""
Tests for notification Celery tasks.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from notifications.models import DeviceToken
from notifications.tasks import cleanup_stale_tokens, send_notification_task
from users.models import CustomUser


def make_user(national_id="29901010100001", phone="01000000001", **kw):
    return CustomUser.objects.create_user(
        national_id=national_id,
        phone_number=phone,
        password="testpass123",
        **kw
    )


@pytest.mark.django_db
class TestSendNotificationTask:
    """Tests for send_notification_task Celery task."""

    @patch('notifications.tasks.send_to_users')
    def test_send_notification_task_dispatches_to_push_service(self, mock_send):
        """Test task calls push service."""
        user = make_user()
        mock_send.return_value = []

        result = send_notification_task.delay(
            user_ids=[str(user.id)],
            event_type="NURSE_ASSIGNED",
            context={"nurse_name": "أحمد"},
        )

        # Wait for task to complete (with CELERY_TASK_ALWAYS_EAGER)
        assert mock_send.called

    @patch('notifications.tasks.send_to_users')
    def test_send_notification_task_handles_multiple_users(self, mock_send):
        """Test task handles multiple users."""
        user1 = make_user(national_id="29901010100002", phone="01000000002")
        user2 = make_user(national_id="29901010100003", phone="01000000003")

        mock_send.return_value = []

        result = send_notification_task.delay(
            user_ids=[str(user1.id), str(user2.id)],
            event_type="NURSE_ASSIGNED",
            context={"nurse_name": "أحمد"},
        )

        assert mock_send.called


@pytest.mark.django_db
class TestCleanupStaleTokens:
    """Tests for cleanup_stale_tokens task."""

    def test_cleanup_stale_tokens_deactivates_old(self):
        """Test stale tokens are deactivated."""
        user = make_user()
        token = DeviceToken.objects.create(
            user=user,
            token="old-token",
            platform="ANDROID",
        )

        # Set last_active to 31 days ago
        DeviceToken.objects.filter(pk=token.pk).update(
            last_active=timezone.now() - timedelta(days=31)
        )

        count = cleanup_stale_tokens()

        assert count == 1
        token.refresh_from_db()
        assert token.is_active is False

    def test_cleanup_stale_tokens_keeps_recent(self):
        """Test recent tokens are not deactivated."""
        user = make_user()
        token = DeviceToken.objects.create(
            user=user,
            token="recent-token",
            platform="ANDROID",
        )

        count = cleanup_stale_tokens()

        assert count == 0
        token.refresh_from_db()
        assert token.is_active is True

    def test_cleanup_stale_tokens_uses_setting(self):
        """Test cleanup uses the configured stale token days."""
        from django.test import override_settings

        user = make_user()
        token = DeviceToken.objects.create(
            user=user,
            token="old-token-2",
            platform="ANDROID",
        )

        # Set to 8 days ago (default is 30, so should keep)
        DeviceToken.objects.filter(pk=token.pk).update(
            last_active=timezone.now() - timedelta(days=8)
        )

        with override_settings(NOTIFICATION_STALE_TOKEN_DAYS=7):
            count = cleanup_stale_tokens()

        assert count == 1
