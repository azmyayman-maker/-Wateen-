from __future__ import annotations

from django.db.models import Avg, F, Count, Q
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import DurationField
from rest_framework.views import APIView
from rest_framework.response import Response

from users.permissions import IsSuperAdmin
from visits.models import Visit, VisitStatus


class DispatchAnalyticsAPIView(APIView):
    """
    SuperAdmin endpoint for dispatch health metrics (US4).
    Uses IsSuperAdmin permission class for proper access control.
    """

    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total_visits = Visit.objects.count()
        if total_visits == 0:
            return Response(
                {
                    "dispatch_success_rate": 0.0,
                    "cancellation_rate": 0.0,
                    "avg_time_to_nurse_assignment": None,
                    "total_visits": 0,
                    "completed_visits": 0,
                    "cancelled_visits": 0,
                }
            )

        total_f = float(total_visits)

        # Dispatch success = visits that reached COMPLETED
        completed_visits = Visit.objects.filter(status=VisitStatus.COMPLETED).count()
        dispatch_success_rate = (completed_visits / total_f) * 100.0

        # Cancellation rate = visits that were CANCELLED (proxy for re-routing)
        cancelled_visits = Visit.objects.filter(status=VisitStatus.CANCELLED).count()
        cancellation_rate = (cancelled_visits / total_f) * 100.0

        # Avg time to nurse assignment (requires nurse_assigned_at field):
        # Falls back to counting visits with nurse assigned but no timestamp (legacy)
        assigned_visits_with_time = Visit.objects.filter(
            nurse_assigned_at__isnull=False
        )
        avg_assignment_time = assigned_visits_with_time.aggregate(
            avg_time=Avg(
                ExpressionWrapper(
                    F("nurse_assigned_at") - F("created_at"),
                    output_field=DurationField(),
                )
            )
        )["avg_time"]

        avg_time_str = None
        avg_minutes = None
        if avg_assignment_time is not None:
            total_seconds = int(avg_assignment_time.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            avg_time_str = f"{minutes}m {seconds}s"
            avg_minutes = round(avg_assignment_time.total_seconds() / 60.0, 2)

        return Response(
            {
                "dispatch_success_rate": round(dispatch_success_rate, 2),
                "cancellation_rate": round(cancellation_rate, 2),
                "avg_time_to_nurse_assignment": avg_time_str,
                "avg_assignment_time_minutes": avg_minutes,
                "total_visits": total_visits,
                "completed_visits": completed_visits,
                "cancelled_visits": cancelled_visits,
            }
        )
