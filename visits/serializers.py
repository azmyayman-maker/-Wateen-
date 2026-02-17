from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class VisitRequestSerializer(serializers.Serializer):
    """Input serializer for creating a visit request."""

    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text=_('خط العرض'),
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text=_('خط الطول'),
    )
    service_type = serializers.CharField(
        max_length=50,
        required=False,
        default='',
        help_text=_('نوع الخدمة'),
    )


class VisitResponseSerializer(serializers.Serializer):
    """Output serializer for visit data."""

    id = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    service_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_latitude(self, obj) -> float:
        return obj.location.y if obj.location else None

    def get_longitude(self, obj) -> float:
        return obj.location.x if obj.location else None
