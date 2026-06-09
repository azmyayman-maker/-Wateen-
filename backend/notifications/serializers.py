"""
DRF Serializers for Notifications API.
"""

from rest_framework import serializers

from notifications.models import DeviceToken, Platform, UserNotificationPrefs


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for DeviceToken model."""

    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "is_active", "last_active", "created_at"]
        read_only_fields = ["id", "is_active", "last_active", "created_at"]

    def validate_platform(self, value):
        """Ensure platform is a valid choice."""
        valid_platforms = [choice[0] for choice in Platform.choices]
        if value not in valid_platforms:
            raise serializers.ValidationError(f"Invalid platform. Must be one of: {valid_platforms}")
        return value

    def create(self, validated_data):
        """Create or update device token (upsert behavior)."""
        validated_data["user"] = self.context["request"].user
        token, created = DeviceToken.objects.update_or_create(
            token=validated_data["token"],
            defaults={**validated_data},
        )
        # Flag for view to determine response status
        self._created = created
        return token


class UserNotificationPrefsSerializer(serializers.ModelSerializer):
    """Serializer for UserNotificationPrefs model."""

    class Meta:
        model = UserNotificationPrefs
        fields = ["visit_updates", "financial_updates", "marketing", "dispatch_offers"]

    def update(self, instance, validated_data):
        """Update user notification preferences."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
