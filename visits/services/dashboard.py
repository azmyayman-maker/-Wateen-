from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from users.models import NurseProfile, AgencyProfile
from visits.models import Visit, VisitStatus, Transaction, TransactionStatus


class AgencyDashboardService:
    @staticmethod
    def get_overview_data(agency: AgencyProfile) -> dict:
        # 1. Real-time stats
        stats = {
            "pending_visits": Visit.objects.filter(
                agency=agency, status=VisitStatus.PENDING_AGENCY
            ).count(),
            "active_visits": Visit.objects.filter(
                agency=agency,
                status__in=[
                    VisitStatus.PENDING_NURSE,
                    VisitStatus.ACCEPTED,
                    VisitStatus.EN_ROUTE,
                    VisitStatus.IN_PROGRESS,
                ],
            ).count(),
            "completed_today": Visit.objects.filter(
                agency=agency,
                status=VisitStatus.COMPLETED,
                updated_at__date=timezone.now().date(),
            ).count(),
            "online_nurses": NurseProfile.objects.filter(
                agency=agency, is_available=True
            ).count(),
            "total_nurses": NurseProfile.objects.filter(agency=agency).count(),
        }

        # 2. Financial summary (computed from actual transactions)
        today = timezone.now().date()
        today_transactions = Transaction.objects.filter(
            agency=agency,
            status=TransactionStatus.SETTLED,
            created_at__date=today,
        ).aggregate(total=Coalesce(Sum("agency_payout"), Decimal("0")))
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

        return {
            "agency_name": agency.manager_name,
            "stats": stats,
            "financials": financials,
            "settings": settings,
            "timestamp": timezone.now(),
        }
