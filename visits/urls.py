from django.urls import path

from .api import EstimateView, MockPaymentWebhookView
from .views import (
    NurseToggleAvailabilityView,
    NursePendingVisitsView,
    NurseRespondVisitView,
)
from .request_views import VisitRequestView
from .dispatch_views import ManualDispatchView
from .dashboard_views import AgencyDashboardOverviewView

app_name = "visits"

urlpatterns = [
    # Patient endpoints
    path("request/", VisitRequestView.as_view(), name="visit_request"),
    path("estimate/", EstimateView.as_view(), name="estimate"),
    path(
        "payments/webhook/mock/", MockPaymentWebhookView.as_view(), name="mock_webhook"
    ),
    # Nurse endpoints
    path("nurse/toggle/", NurseToggleAvailabilityView.as_view(), name="nurse_toggle"),
    path("nurse/pending/", NursePendingVisitsView.as_view(), name="nurse_pending"),
    path("nurse/respond/", NurseRespondVisitView.as_view(), name="nurse_respond"),
    
    # Agency/Dispatch endpoints
    path("agency/<uuid:agency_id>/dispatch/manual/", ManualDispatchView.as_view(), name="agency_dispatch_manual"),
    path("agency/<uuid:agency_id>/dashboard/overview/", AgencyDashboardOverviewView.as_view(), name="agency_dashboard_overview"),
]

