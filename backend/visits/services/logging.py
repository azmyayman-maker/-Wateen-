"""
Logging Service for Visits App.

Handles asynchronous logging of estimates and other events
to avoid circular imports and keep API/Signals clean.
"""

import logging
from datetime import datetime
from typing import Any

from django.contrib.gis.geos import Point
from django.db import transaction

from visits.models import EstimateLog, ServiceType

logger = logging.getLogger(__name__)

def log_estimate_request(
    service_type_id: str,
    latitude: float,
    longitude: float,
    request_time: datetime,
    price_components: dict[str, Any],
    ip_address: str | None = None,
) -> None:
    """
    Log an estimate request for AI training data.

    Creates an EstimateLog entry with all relevant data for future
    machine learning model training. Uses transaction.on_commit()
    to ensure logging happens asynchronously after the main transaction
    completes, avoiding blocking the API response.

    Args:
        service_type_id: UUID of the requested service type
        latitude: Customer latitude
        longitude: Customer longitude
        request_time: When the estimate was requested
        price_components: Dict with price breakdown (base_price, distance_km, etc.)
        ip_address: Client IP address (optional)
    """

    def do_log():
        try:
            service_type = ServiceType.objects.get(id=service_type_id)
        except ServiceType.DoesNotExist:
            service_type = None
            logger.warning(
                "ServiceType %s not found during logging.", service_type_id
            )

        EstimateLog.objects.create(
            request_time=request_time,
            location=Point(longitude, latitude, srid=4326),
            service_type=service_type,
            price_components=price_components,
            ip_address=ip_address,
        )

    transaction.on_commit(do_log)
