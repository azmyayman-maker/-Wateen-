from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from visits.models import Visit, VisitStatus, Transaction, TransactionStatus
from users.models import NurseProfile, AgencyProfile


class AgencyDashboardOverviewView(generics.GenericAPIView):
    """
    GET /api/v1/agency/{agency_id}/dashboard/overview
    Provides statistics and real-time counts for the agency dashboard.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        agency_id = self.kwargs.get("agency_id")

        # Verify agency exists
        try:
            agency = AgencyProfile.objects.get(id=agency_id)
        except AgencyProfile.DoesNotExist:
            return Response({"detail": "Agency not found."}, status=404)

        # 1. Real-time stats
        stats = {
            "pending_visits": Visit.objects.filter(
                agency_id=agency_id, status=VisitStatus.PENDING_AGENCY
            ).count(),
            "active_visits": Visit.objects.filter(
                agency_id=agency_id,
                status__in=[
                    VisitStatus.PENDING_NURSE,
                    VisitStatus.ACCEPTED,
                    VisitStatus.EN_ROUTE,
                    VisitStatus.IN_PROGRESS,
                ],
            ).count(),
            "completed_today": Visit.objects.filter(
                agency_id=agency_id,
                status=VisitStatus.COMPLETED,
                updated_at__date=timezone.now().date(),
            ).count(),
            "online_nurses": NurseProfile.objects.filter(
                agency_id=agency_id, is_available=True
            ).count(),
            "total_nurses": NurseProfile.objects.filter(agency_id=agency_id).count(),
        }

        # 2. Financial summary (computed from actual transactions)
        today = timezone.now().date()
        today_transactions = Transaction.objects.filter(
            visit__agency_id=agency_id,
            status=TransactionStatus.SETTLED,
            created_at__date=today,
        ).aggregate(total=Coalesce(Sum("agency_amount"), Decimal("0")))
        daily_revenue = today_transactions["total"]

        financials = {
            "daily_revenue": str(daily_revenue.quantize(Decimal("0.01"))),
            "wallet_balance": str(agency.wallet_balance.quantize(Decimal("0.01"))),
        }

        # 3. Agency settings summary
        settings = {
            "dispatch_mode": agency.dispatch_mode,
            "has_coverage": agency.coverage_polygon is not None,
        }

        return Response(
            {
                "agency_name": agency.manager_name,
                "stats": stats,
                "financials": financials,
                "settings": settings,
                "timestamp": timezone.now(),
            }
        )
