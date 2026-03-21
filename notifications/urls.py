"""
URL Configuration for Notifications API.
"""

from rest_framework.routers import DefaultRouter
from django.urls import path

from notifications.views import DeviceTokenViewSet, NotificationPrefsView

router = DefaultRouter()
router.register("devices", DeviceTokenViewSet, basename="device-token")

urlpatterns = router.urls + [
    path("preferences/", NotificationPrefsView.as_view(), name="notification-preferences"),
]
