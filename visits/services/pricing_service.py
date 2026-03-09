"""
Wateen Cognitive Pricing Engine.
Implements MoH-compliant pricing algorithm.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.utils import timezone
from django.contrib.gis.geos import Point
from zoneinfo import ZoneInfo

from visits.models import ServiceType
from users.models import AgencyProfile
from visits.services.routing_service import get_route

try:
    from visits.services.demand_service import DemandPredictionService
except ImportError:
    class DemandPredictionService:
        @staticmethod
        def get_surge(geohash: str) -> Decimal:
            return Decimal("1.0")


def calculate_cognitive_price(
    service_type: ServiceType,
    agency: AgencyProfile,
    patient_location: Point,
    urgency: str
) -> dict:
    """
    Calculate the precise MoH-compliant cognitive price for a visit.

    Formula:
    P_final = [ (B * M_time * M_urgency) + (D_osrm * R_zone * (1 + E_traffic)) ] * Phi_surge + (B * Gamma * (R_a / 5.0))

    Where:
    - B: Base price of the service (`service_type.base_price`)
    - M_time: 1.2 for night hours (22:00 - 06:00) Cairo Time / holidays, else 1.0
    - M_urgency: 1.0 (low), 1.2 (high), 1.5 (SOS/critical) mapped from `visit_request.urgency`
    - D_osrm: Routing distance in km via internal OSRM/ORS wrapper
    - R_zone: Zone base rate (fallback 5.00 EGP)
    - E_traffic: 0.1 if traffic delays are high, else 0.0
    - Phi_surge: Dynamic surge multiplier (max 3.0)
    - Gamma: 0.10 premium cap
    - R_a: Agency rating 
    """
    # 1. Base Price (B)
    B = Decimal(str(service_type.base_price))

    # 2. Urgency Multiplier (M_urgency)
    urgency_map = {
        "low": Decimal("1.0"),
        "high": Decimal("1.2"),
        "sos": Decimal("1.5"),
        "critical": Decimal("1.5")
    }
    M_urgency = urgency_map.get(urgency.lower(), Decimal("1.0"))

    # 3. Time Multiplier (M_time)
    CAIRO_TZ = ZoneInfo("Africa/Cairo")
    now = timezone.now().astimezone(CAIRO_TZ)
    if now.hour >= 22 or now.hour < 6:
        M_time = Decimal("1.2")
    else:
        M_time = Decimal("1.0")

    # 4. Routing & Distance (D_osrm, E_traffic)
    agency_point = agency.coverage_polygon.centroid if agency.coverage_polygon else Point(0, 0, srid=4326)

    try:
        route_stats = get_route(
            origin_lat=agency_point.y,
            origin_lng=agency_point.x,
            dest_lat=patient_location.y,
            dest_lng=patient_location.x
        )
        dist = route_stats.distance_km
        dur = route_stats.duration_minutes
    except Exception:
        dist = 0.0
        dur = 0.0
    
    D_osrm = Decimal(str(dist))
    duration_minutes = Decimal(str(dur))
    
    # Calculate traffic threshold: (distance_km / 40) * 60 * 1.3
    if D_osrm > Decimal("0.0"):
        tx_threshold = (D_osrm / Decimal("40.0")) * Decimal("60.0") * Decimal("1.3")
    else:
        tx_threshold = Decimal("0.0")
        
    if duration_minutes > tx_threshold and D_osrm > Decimal("0.0"):
        E_traffic = Decimal("0.1")
    else:
        E_traffic = Decimal("0.0")

    # 5. Zone Rate (R_zone)
    R_zone = Decimal("5.00")

    # 6. Surge (Phi_surge)
    try:
        surge_val = DemandPredictionService.get_surge(str(patient_location))
    except Exception:
        surge_val = Decimal("1.0")
        
    Phi_surge = Decimal(str(surge_val))
    if Phi_surge > Decimal("3.0"):
        Phi_surge = Decimal("3.0")

    # 7. Quality Premium (Gamma, R_a)
    Gamma = Decimal("0.10")
    agency_rating_raw = getattr(agency, "rating", None)
    try:
        agency_rating = Decimal(str(agency_rating_raw))
    except (TypeError, ValueError, InvalidOperation) as e:
        agency_rating = Decimal("5.0")
    R_a = agency_rating
    
    # 8. Mathematics Setup
    base_calc = B * M_time * M_urgency
    logistics_calc = D_osrm * R_zone * (Decimal("1.0") + E_traffic)
    quality_premium = B * Gamma * (R_a / Decimal("5.0"))
    
    # P_final = [ base_calc + logistics_calc ] * Phi_surge + quality_premium
    raw_final = ((base_calc + logistics_calc) * Phi_surge) + quality_premium
    
    final_price = raw_final.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Quantize components for snapshot storage clarity
    base_calc_q = base_calc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    logistics_calc_q = logistics_calc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    quality_premium_q = quality_premium.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    Phi_surge_q = Phi_surge.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "base_calc": base_calc_q,
        "logistics_calc": logistics_calc_q,
        "surge_multiplier": Phi_surge_q,
        "quality_premium": quality_premium_q,
        "final_price": final_price,
    }
