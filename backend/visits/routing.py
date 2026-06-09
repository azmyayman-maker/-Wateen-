"""
WebSocket URL routing for the visits app.
"""

from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/test/$", consumers.TestConsumer.as_asgi()),
    re_path(r"ws/patient/$", consumers.PatientConsumer.as_asgi()),
    re_path(r"ws/nurse/$", consumers.NurseConsumer.as_asgi()),
    re_path(r"ws/agency/$", consumers.AgencyConsumer.as_asgi()),
    re_path(r"ws/dashboard/$", consumers.DashboardMetricsConsumer.as_asgi()),
    re_path(r"ws/nurse-gps/$", consumers.NurseGPSConsumer.as_asgi()),
    path(
        "ws/agency/<uuid:agency_id>/dashboard/",
        consumers.AgencyDashboardConsumer.as_asgi(),
    ),
    path("ws/visits/<uuid:visit_id>/", consumers.VisitConsumer.as_asgi()),
]
