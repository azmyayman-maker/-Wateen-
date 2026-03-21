"""
API Views for Notifications.
"""

from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView

from notifications.models import DeviceToken, UserNotificationPrefs
from notifications.serializers import DeviceTokenSerializer, UserNotificationPrefsSerializer


class DeviceTokenViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for managing device tokens."""
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "token"
    
    def get_queryset(self):
        """Return only active tokens for the current user."""
        return DeviceToken.objects.filter(
            user=self.request.user,
            is_active=True,
        )
    
    def create(self, request, *args, **kwargs):
        """Create or update device token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Determine response status based on whether it was created or updated
        if hasattr(serializer, '_created') and not serializer._created:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        """Save the serializer with the current user."""
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Deactivate a device token (soft delete)."""
        token = kwargs.get("token")
        try:
            device_token = DeviceToken.objects.get(
                token=token,
                user=request.user,
            )
            device_token.is_active = False
            device_token.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DeviceToken.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class NotificationPrefsView(RetrieveUpdateAPIView):
    """View for retrieving and updating notification preferences."""
    
    serializer_class = UserNotificationPrefsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]
    
    def get_object(self):
        """Get or create notification preferences for the current user."""
        prefs, _ = UserNotificationPrefs.objects.get_or_create(
            user=self.request.user,
        )
        return prefs
