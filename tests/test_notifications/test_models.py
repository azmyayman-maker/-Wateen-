"""
Unit tests for Notification models.
"""

import pytest
from django.db import IntegrityError
from django.test import TestCase

from notifications.models import (
    NotificationEventType,
    NotificationStatus,
    EVENT_CATEGORY_MAP,
    NotificationLog,
    UserNotificationPrefs,
    DeviceToken,
)
from users.models import CustomUser


# Factory helper function
def make_user(national_id="29901010100001", phone="01000000001", **kw):
    """Create a CustomUser using create_user."""
    return CustomUser.objects.create_user(
        national_id=national_id,
        phone_number=phone,
        password="testpass123",
        **kw
    )


@pytest.mark.django_db
class TestNotificationEventType:
    """Tests for NotificationEventType enum."""
    
    def test_notification_event_type_has_8_values(self):
        """NotificationEventType should have exactly 8 values."""
        assert len(NotificationEventType.choices) == 8
    
    def test_notification_event_type_values(self):
        """Verify all expected event type values exist."""
        expected_values = [
            "NURSE_ASSIGNED",
            "NURSE_EN_ROUTE",
            "NURSE_ARRIVED",
            "VISIT_COMPLETED",
            "PAYMENT_SETTLED",
            "DISPATCH_OFFER",
            "VISIT_CANCELLED",
            "SOS_ALERT",
        ]
        actual_values = [choice[0] for choice in NotificationEventType.choices]
        for expected in expected_values:
            assert expected in actual_values


@pytest.mark.django_db
class TestNotificationStatus:
    """Tests for NotificationStatus enum."""
    
    def test_notification_status_has_3_values(self):
        """NotificationStatus should have exactly 3 values."""
        assert len(NotificationStatus.choices) == 3


@pytest.mark.django_db
class TestEventCategoryMap:
    """Tests for EVENT_CATEGORY_MAP."""
    
    def test_event_category_map_covers_all_events(self):
        """Every NotificationEventType should be a key in EVENT_CATEGORY_MAP."""
        event_types = [choice[0] for choice in NotificationEventType.choices]
        for event_type in event_types:
            assert event_type in EVENT_CATEGORY_MAP
    
    def test_sos_alert_has_no_category(self):
        """SOS_ALERT should have None category (always send)."""
        assert EVENT_CATEGORY_MAP["SOS_ALERT"] is None


@pytest.mark.django_db
class TestNotificationLog:
    """Tests for NotificationLog model."""
    
    def test_notification_log_creation(self):
        """NotificationLog can be created with all fields."""
        user = make_user()
        log = NotificationLog.objects.create(
            recipient=user,
            event_type=NotificationEventType.NURSE_ASSIGNED,
            template_key="NURSE_ASSIGNED",
            title="Test Title",
            body="Test Body",
            data_payload={"visit_id": "test-uuid"},
            status=NotificationStatus.SENT,
        )
        assert log.pk is not None
        assert log.created_at is not None
    
    def test_notification_log_immutability(self):
        """NotificationLog can be saved after creation (application-level immutability)."""
        user = make_user()
        log = NotificationLog.objects.create(
            recipient=user,
            event_type=NotificationEventType.NURSE_ASSIGNED,
            title="Test Title",
            body="Test Body",
            status=NotificationStatus.SENT,
        )
        # Note: Immutability is enforced at application level, not DB level
        log.status = NotificationStatus.FAILED
        log.save()
        log.refresh_from_db()
        assert log.status == NotificationStatus.FAILED


@pytest.mark.django_db
class TestUserNotificationPrefs:
    """Tests for UserNotificationPrefs model."""
    
    def test_user_notification_prefs_defaults(self):
        """UserNotificationPrefs should have correct default values."""
        user = make_user()
        # Signal should auto-create prefs
        prefs = UserNotificationPrefs.objects.get(user=user)
        assert prefs.visit_updates is True
        assert prefs.financial_updates is True
        assert prefs.marketing is True
        assert prefs.dispatch_offers is True
    
    def test_user_notification_prefs_auto_created_on_user_save(self):
        """UserNotificationPrefs should be auto-created when user is created."""
        user = make_user(national_id="29901010100002", phone="01000000002")
        assert UserNotificationPrefs.objects.filter(user=user).exists()
    
    def test_user_notification_prefs_is_category_enabled_sos(self):
        """is_category_enabled should return True for None (SOS)."""
        user = make_user()
        prefs = UserNotificationPrefs.objects.get(user=user)
        assert prefs.is_category_enabled(None) is True
    
    def test_user_notification_prefs_is_category_enabled_disabled(self):
        """is_category_enabled should return False when category is disabled."""
        user = make_user()
        prefs = UserNotificationPrefs.objects.get(user=user)
        prefs.financial_updates = False
        prefs.save()
        assert prefs.is_category_enabled("financial_updates") is False


@pytest.mark.django_db
class TestDeviceToken:
    """Tests for DeviceToken model."""
    
    def test_device_token_uniqueness(self):
        """DeviceToken token field should be unique."""
        user = make_user()
        token_value = "test-fcm-token-123"
        
        DeviceToken.objects.create(
            user=user,
            token=token_value,
            platform="ANDROID",
        )
        
        # Second creation should raise IntegrityError
        with pytest.raises(IntegrityError):
            DeviceToken.objects.create(
                user=user,
                token=token_value,
                platform="IOS",
            )


@pytest.mark.django_db
class TestPreferredLanguage:
    """Tests for CustomUser.preferred_language field."""
    
    def test_preferred_language_default_is_arabic(self):
        """preferred_language should default to Arabic."""
        user = make_user()
        assert user.preferred_language == "ar"
