"""
Notifications Models — Device tokens for push notifications.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Platform(models.TextChoices):
    WEB = "WEB", _("ويب")
    ANDROID = "ANDROID", _("أندرويد")
    IOS = "IOS", _("آيفون")


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
