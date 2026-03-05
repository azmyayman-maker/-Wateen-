"""
WebSocket URL routing for the visits app.
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/test/$', consumers.TestConsumer.as_asgi()),
    re_path(r'ws/patient/$', consumers.PatientConsumer.as_asgi()),
    re_path(r'ws/nurse/$', consumers.NurseConsumer.as_asgi()),
    re_path(r'ws/agency/$', consumers.AgencyConsumer.as_asgi()),
    re_path(r'ws/dashboard/$', consumers.DashboardMetricsConsumer.as_asgi()),
    re_path(r'ws/nurse-gps/$', consumers.NurseGPSConsumer.as_asgi()),
]
