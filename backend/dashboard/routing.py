from django.urls import re_path

from .consumers import agency_consumer, superadmin_consumer

websocket_urlpatterns = [
    re_path(r'ws/dashboard/agency/$', agency_consumer.DashboardMetricsConsumer.as_asgi()),
    re_path(r'ws/dashboard/superadmin/$', superadmin_consumer.SuperAdminCommandConsumer.as_asgi()),
]
