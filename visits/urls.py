from django.urls import path

from .api import EstimateView, MockPaymentWebhookView
from .views import VisitRequestView

app_name = "visits"

urlpatterns = [
    path("request/", VisitRequestView.as_view(), name="visit_request"),
    path("estimate/", EstimateView.as_view(), name="estimate"),
    path(
        "payments/webhook/mock/", MockPaymentWebhookView.as_view(), name="mock_webhook"
    ),
]
