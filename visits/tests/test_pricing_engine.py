import pytest
from django.utils import timezone
from datetime import datetime, time
from rest_framework import status
from decimal import Decimal
from zoneinfo import ZoneInfo
from visits.models import PricingFactor

CAIRO_TZ = ZoneInfo("Africa/Cairo")

pytestmark = pytest.mark.django_db

def test_estimate_api_daytime(api_client, service_type):
    """
    Test the estimate API during day time (e.g., 14:00 PM).
    """
    # Set up pricing factors defaults in DB if needed to match expectations
    PricingFactor.objects.update_or_create(key="per_km_rate", defaults={"value": "20.00"})
    PricingFactor.objects.update_or_create(key="day_multiplier", defaults={"value": "1.00"})
    PricingFactor.objects.update_or_create(key="night_start_hour", defaults={"value": "22"})
    PricingFactor.objects.update_or_create(key="night_end_hour", defaults={"value": "6"})

    url = "/api/v1/visits/estimate/"
    
    day_time = datetime.combine(timezone.now().date(), time(14, 0)).replace(tzinfo=CAIRO_TZ)
    
    data = {
        "service_type_id": str(service_type.id),
        "latitude": 30.0440,
        "longitude": 31.2350,
        "request_time": day_time.isoformat()
    }
    
    # Needs nearest nurse logic, assuming distance returns a simple float if default function exists OR mock find_nearest_available_nurse.
    # We will test the API directly which integrates everything.
    response = api_client.post(url, data, format="json")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    
    assert data["currency"] == "EGP"
    assert data["is_night_hours"] is False
    assert "breakdown" in data
    
    breakdown = data["breakdown"]
    assert str(breakdown["base_price"]) == str(service_type.base_price)
    # The final price should reflect no night multiplier.

def test_estimate_api_night_time_premium(api_client, service_type):
    """
    Test the estimate API during night time (e.g., 03:00 AM) applying the premium.
    """
    PricingFactor.objects.update_or_create(key="per_km_rate", defaults={"value": "20.00"})
    PricingFactor.objects.update_or_create(key="night_multiplier", defaults={"value": "1.50"})
    PricingFactor.objects.update_or_create(key="night_start_hour", defaults={"value": "22"})
    PricingFactor.objects.update_or_create(key="night_end_hour", defaults={"value": "6"})

    url = "/api/v1/visits/estimate/"
    
    night_time = datetime.combine(timezone.now().date(), time(3, 0)).replace(tzinfo=CAIRO_TZ)
    
    data = {
        "service_type_id": str(service_type.id),
        "latitude": 30.0440,
        "longitude": 31.2350,
        "request_time": night_time.isoformat()
    }
    
    response = api_client.post(url, data, format="json")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_night_hours"] is True
    
    breakdown = response.data["breakdown"]
    assert Decimal(breakdown["time_multiplier"]) == Decimal("1.50")
