from django.urls import path

from .api import EstimateView, MockPaymentWebhookView, PaymentIntentView, PaymobWebhookView
from .views import (
    NurseToggleAvailabilityView,
    NursePendingVisitsView,
    NurseRespondVisitView,
    NurseRespondOfferView,
    VisitStatusView,
    VisitTransitionView,
    PatientRequestVisitView,
)
from .dispatch_views import ManualDispatchView
from .dashboard_views import AgencyDashboardOverviewView
from .geo_views import GeoDiagnosticsView
from .admin_views import DispatchAnalyticsAPIView

app_name = "visits"

urlpatterns = [
    # Admin endpoints
    path("admin/dispatch-analytics/", DispatchAnalyticsAPIView.as_view(), name="dispatch_analytics"),

    # Geo diagnostics (SuperAdmin only)
    path("geo/diagnostics/", GeoDiagnosticsView.as_view(), name="geo-diagnostics"),
    
    # Patient endpoints
    path("request/", PatientRequestVisitView.as_view(), name="visit_request"),
    path("estimate/", EstimateView.as_view(), name="estimate"),
    path(
        "payments/webhook/mock/", MockPaymentWebhookView.as_view(), name="mock_webhook"
    ),
    # Nurse endpoints
    path("nurse/toggle/", NurseToggleAvailabilityView.as_view(), name="nurse_toggle"),
    path("nurse/pending/", NursePendingVisitsView.as_view(), name="nurse_pending"),
    path("nurse/respond/", NurseRespondVisitView.as_view(), name="nurse_respond"),
    path("nurse/respond-offer/", NurseRespondOfferView.as_view(), name="nurse_respond_offer"),
    
    # Agency/Dispatch endpoints
    path("agency/<uuid:agency_id>/dispatch/manual/", ManualDispatchView.as_view(), name="agency_dispatch_manual"),
    path("agency/<uuid:agency_id>/dashboard/overview/", AgencyDashboardOverviewView.as_view(), name="agency_dashboard_overview"),

    # Payment endpoints
    path("payments/intent/", PaymentIntentView.as_view(), name="payment_intent"),
    path("webhooks/paymob/", PaymobWebhookView.as_view(), name="paymob_webhook"),

    # Status polling
    path("<uuid:visit_id>/status/", VisitStatusView.as_view(), name="visit_status"),
    path("<uuid:visit_id>/transition/", VisitTransitionView.as_view(), name="visit_transition"),
]
