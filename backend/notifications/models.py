"""
Notifications Models — Device tokens, notification logs, and user preferences for push notifications.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Platform(models.TextChoices):
    WEB = "WEB", _("ويب")
    ANDROID = "ANDROID", _("أندرويد")
    IOS = "IOS", _("آي أو إس")


class NotificationEventType(models.TextChoices):
    """Event types for push notifications."""
    NURSE_ASSIGNED = "NURSE_ASSIGNED", _("تم تعيين الممرض/ة")
    NURSE_EN_ROUTE = "NURSE_EN_ROUTE", _("الممرض/ة في الطريق")
    NURSE_ARRIVED = "NURSE_ARRIVED", _("وصلت الممرض/ة")
    VISIT_COMPLETED = "VISIT_COMPLETED", _("اكتملت الزيارة")
    PAYMENT_SETTLED = "PAYMENT_SETTLED", _("تمت التسوية المالية")
    DISPATCH_OFFER = "DISPATCH_OFFER", _("عرض زيارة جديد")
    VISIT_CANCELLED = "VISIT_CANCELLED", _("تم إلغاء الزيارة")
    SOS_ALERT = "SOS_ALERT", _("تنبيه طوارئ")


class NotificationStatus(models.TextChoices):
    """Status of notification delivery."""
    SENT = "SENT", _("تم الإرسال")
    FAILED = "FAILED", _("فشل")
    SKIPPED = "SKIPPED", _("تم التخطي")


# Category mapping for user preference filtering
EVENT_CATEGORY_MAP = {
    "NURSE_ASSIGNED": "visit_updates",
    "NURSE_EN_ROUTE": "visit_updates",
    "NURSE_ARRIVED": "visit_updates",
    "VISIT_COMPLETED": "visit_updates",
    "PAYMENT_SETTLED": "financial_updates",
    "DISPATCH_OFFER": "dispatch_offers",
    "VISIT_CANCELLED": "visit_updates",
    "SOS_ALERT": None,  # None = always send, bypass preferences
}


class DeviceToken(models.Model):
    """
    Stores push notification tokens for user devices.
    Each user can have multiple devices (phone + web PWA).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_tokens",
    )
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(
        max_length=10,
        choices=Platform.choices,
        default=Platform.WEB,
    )
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_active"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"Device({self.platform}) → {self.user_id}"


class NotificationLog(models.Model):
    """
    Immutable audit log for all push notifications sent through the system.
    Records the event type, rendered content, delivery status, and any errors.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_logs",
    )
    event_type = models.CharField(
        max_length=50,
        choices=NotificationEventType.choices,
        db_index=True,
    )
    template_key = models.CharField(max_length=50, blank=True, default="")
    title = models.CharField(max_length=255, blank=True, default="")
    body = models.TextField(blank=True, default="")
    data_payload = models.JSONField(default=dict)
    status = models.CharField(
        max_length=10,
        choices=NotificationStatus.choices,
        db_index=True,
    )
    fcm_error = models.TextField(blank=True, default="")
    device_token_used = models.CharField(max_length=512, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications_log"
        ordering = ["-created_at"]
        verbose_name = _("سجل الإشعار")
        verbose_name_plural = _("سجلات الإشعارات")
        indexes = [
            models.Index(fields=["recipient", "created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"NotifLog({self.event_type}→{self.recipient_id} [{self.status}])"


class UserNotificationPrefs(models.Model):
    """
    User preferences for push notifications.
    One-to-one relationship with CustomUser.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="notification_prefs",
    )
    visit_updates = models.BooleanField(
        default=True,
        verbose_name=_("تحديثات الزيارات"),
    )
    financial_updates = models.BooleanField(
        default=True,
        verbose_name=_("التحديثات المالية"),
    )
    marketing = models.BooleanField(
        default=True,
        verbose_name=_("الإشعارات التسويقية"),
    )
    dispatch_offers = models.BooleanField(
        default=True,
        verbose_name=_("عروض التوزيع"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications_user_prefs"
        verbose_name = _("تفضيلات الإشعارات")
        verbose_name_plural = _("تفضيلات إشعارات المستخدمين")

    def __str__(self):
        return f"NotifPrefs({self.user_id})"

    def is_category_enabled(self, category: str | None) -> bool:
        """
        Check if a notification category is enabled for this user.
        Returns True if category is None (SOS bypass per FR-016).
        """
        if category is None:
            return True
        return getattr(self, category, True)
