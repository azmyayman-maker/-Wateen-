"""
Django Admin configuration for Notifications app.
"""

from django.contrib import admin

from notifications.models import DeviceToken, NotificationLog, UserNotificationPrefs


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin for NotificationLog - read-only audit log."""

    list_display = ("event_type", "recipient", "status", "template_key", "created_at")
    list_filter = ("status", "event_type", "created_at")
    search_fields = ("recipient__national_id", "event_type", "fcm_error")
    readonly_fields = (
        "id", "recipient", "event_type", "template_key", "title",
        "body", "data_payload", "status", "fcm_error", "device_token_used", "created_at",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserNotificationPrefs)
class UserNotificationPrefsAdmin(admin.ModelAdmin):
    """Admin for UserNotificationPrefs."""

    list_display = ("user", "visit_updates", "financial_updates", "marketing", "dispatch_offers", "updated_at")
    list_filter = ("visit_updates", "financial_updates", "marketing")
    search_fields = ("user__national_id",)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """Admin for DeviceToken."""

    list_display = ("user", "platform", "is_active", "last_active", "created_at")
    list_filter = ("platform", "is_active")
    search_fields = ("user__national_id",)
    readonly_fields = ("token",)
