"""
Pricing Engine Service for Wateen.

Implements rule-based pricing strategy with:
- Distance-based fees
- Day/Night multipliers
- AI-ready surge coefficient placeholder

RTL-compatible error messages in Arabic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import logging
from typing import Optional
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

# Cairo timezone for consistent pricing calculations
CAIRO_TZ = ZoneInfo("Africa/Cairo")


@dataclass
class PriceResult:
    """Result of a price calculation with breakdown."""

    base_price: Decimal
    distance_km: Decimal
    distance_fee: Decimal
    time_multiplier: Decimal
    ai_surge_coefficient: Decimal
    final_price: Decimal


# Alias for backward compatibility
PriceBreakdown = PriceResult


class PricingStrategy(ABC):
    """
    Abstract base class for pricing strategies.

    Implementations can provide different pricing algorithms:
    - RuleBasedPricingStrategy: Deterministic rules (day/night, distance)
    - MLPricingStrategy: Machine learning-based dynamic pricing (future)
    """

    @abstractmethod
    def calculate_price(
        self,
        base_price: Decimal,
        distance_km: Decimal,
        request_time: datetime,
        **kwargs,
    ) -> PriceResult:
        """
        Calculate the estimated price for a visit.

        Args:
            base_price: Base price for the service type
            distance_km: Distance to travel in kilometers
            request_time: When the visit is requested
            **kwargs: Additional parameters for pricing

        Returns:
            PriceResult with full breakdown of the calculation.
        """
        pass


class RuleBasedPricingStrategy(PricingStrategy):
    """
    Rule-based pricing strategy for visit estimates.

    Pricing Formula:
        final_price = (base_price + distance_fee) * time_multiplier * ai_surge_coefficient

    Where:
        - distance_fee = distance_km * per_km_rate
        - time_multiplier = night_multiplier (22:00-06:00) or day_multiplier
        - ai_surge_coefficient = 1.0 (placeholder for ML model)
    """

    # Default values when PricingFactor records don't exist
    DEFAULTS = {
        "per_km_rate": Decimal("50.00"),
        "night_multiplier": Decimal("1.50"),
        "day_multiplier": Decimal("1.00"),
        "night_start_hour": Decimal("22"),
        "night_end_hour": Decimal("6"),
        "base_distance_km": Decimal("5"),
    }

    def get_factor(self, key: str) -> Decimal:
        """
        Get a pricing factor value from database or return default.

        Args:
            key: The pricing factor key (e.g., 'per_km_rate')

        Returns:
            The factor value as Decimal, or default if not found.
        """
        try:
            from visits.models import PricingFactor

            factor = PricingFactor.objects.filter(key=key).first()
            if factor:
                return factor.value
        except Exception as e:
            logger.warning("Failed to fetch PricingFactor '%s': %s", key, e)

        return self.DEFAULTS.get(key, Decimal("0"))

    def _is_night_hours(self, request_time: datetime) -> bool:
        """
        Check if the given time falls within night hours.

        Night hours are defined as 22:00 to 06:00 in Cairo timezone.

        Args:
            request_time: The datetime to check (will be converted to Cairo timezone)

        Returns:
            True if within night hours, False otherwise.
        """
        night_start = int(self.get_factor("night_start_hour"))
        night_end = int(self.get_factor("night_end_hour"))

        # Convert to Cairo timezone for consistent pricing
        if request_time.tzinfo is None:
            # Assume naive datetime is in Cairo timezone
            cairo_time = request_time.replace(tzinfo=CAIRO_TZ)
        else:
            cairo_time = request_time.astimezone(CAIRO_TZ)

        hour = cairo_time.hour

        # Night hours span midnight (e.g., 22:00 to 06:00)
        if night_start > night_end:
            return hour >= night_start or hour < night_end
        else:
            return night_start <= hour < night_end

    def is_night_hours(self, request_time: datetime) -> bool:
        """
        Public method to check if the given time falls within night hours.

        Args:
            request_time: The datetime to check (will be converted to Cairo timezone)

        Returns:
            True if within night hours, False otherwise.
        """
        return self._is_night_hours(request_time)

    def get_time_multiplier(self, request_time: datetime) -> Decimal:
        """
        Get the time-based multiplier for a given request time.

        Public method for API and test access to time multiplier logic.

        Args:
            request_time: The datetime to check (will be converted to Cairo timezone)

        Returns:
            The time multiplier (night_multiplier or day_multiplier).
        """
        if self._is_night_hours(request_time):
            return self.get_factor("night_multiplier")
        return self.get_factor("day_multiplier")

    def calculate_price(
        self,
        base_price: Decimal,
        distance_km: Decimal,
        request_time: datetime,
        ai_surge_coefficient: Optional[Decimal] = None,
        **kwargs,
    ) -> PriceResult:
        """
        Calculate the estimated price for a visit.

        Args:
            base_price: Base price for the service type
            distance_km: Distance to travel in kilometers
            request_time: When the visit is requested (affects time multiplier)
            ai_surge_coefficient: Optional surge coefficient (defaults to 1.0)

        Returns:
            PriceResult with full breakdown of the calculation.
        """
        # Coerce all numeric inputs to Decimal
        base_price = Decimal(str(base_price))
        distance_km = Decimal(str(distance_km))
        
        if ai_surge_coefficient is not None:
            ai_surge_coefficient = Decimal(str(ai_surge_coefficient))
            if ai_surge_coefficient > Decimal("3.0"):
                logger.warning("Surge coefficient %.2f exceeds max 3.0. Capping.", ai_surge_coefficient)
                ai_surge_coefficient = Decimal("3.0")
        else:
            ai_surge_coefficient = Decimal("1.0")

        # Impose rigorous bounds
        if base_price <= Decimal("0"):
            raise ValueError("Base price must be strictly positive.")
        if distance_km < Decimal("0"):
            raise ValueError("Distance cannot be negative.")
        if ai_surge_coefficient < Decimal("0"):
            raise ValueError("Surge coefficient cannot be negative.")

        # Get pricing factors
        per_km_rate = self.get_factor("per_km_rate")
        if per_km_rate < Decimal("0"):
            raise ValueError("Per kilometer rate cannot be negative.")

        # Determine time multiplier based on day/night
        if self._is_night_hours(request_time):
            time_multiplier = self.get_factor("night_multiplier")
        else:
            time_multiplier = self.get_factor("day_multiplier")
            
        if time_multiplier <= Decimal("0"):
            raise ValueError("Time multiplier must be strictly positive.")

        # Calculate distance fee (D * R_km)
        distance_fee = (distance_km * per_km_rate).quantize(Decimal("0.01"))

        # Calculate base (B + D*R_km)
        subtotal = base_price + distance_fee

        # Calculate final price precisely: P = (B + D × R_km) * T * S_ai
        final_price = (subtotal * time_multiplier * ai_surge_coefficient).quantize(
            Decimal("0.01")
        )

        return PriceResult(
            base_price=base_price,
            distance_km=distance_km,
            distance_fee=distance_fee,
            time_multiplier=time_multiplier,
            ai_surge_coefficient=ai_surge_coefficient,
            final_price=final_price,
        )


class MLPricingStrategy(PricingStrategy):
    """
    Machine Learning-based pricing strategy (placeholder for future implementation).

    This strategy will use trained ML models to predict optimal pricing
    based on historical data, demand patterns, and external factors.

    For now, it delegates to RuleBasedPricingStrategy.
    """

    def __init__(self):
        self._fallback = RuleBasedPricingStrategy()

    def calculate_price(
        self,
        base_price: Decimal,
        distance_km: Decimal,
        request_time: datetime,
        **kwargs,
    ) -> PriceResult:
        """
        Calculate price using ML model (currently falls back to rule-based).

        TODO: Implement ML-based pricing when model is trained.
        """
        # For now, use rule-based pricing
        return self._fallback.calculate_price(
            base_price=base_price,
            distance_km=distance_km,
            request_time=request_time,
            **kwargs,
        )


def get_default_strategy() -> PricingStrategy:
    """
    Get the default pricing strategy.

    Returns RuleBasedPricingStrategy for MVP.
    Future versions may return MLPricingStrategy based on configuration.
    """
    return RuleBasedPricingStrategy()


# =============================================================================
# Convenience function for simple price calculations
# =============================================================================


def calculate_price(
    service_type,
    distance_km: Decimal,
    time_of_day_multiplier: Decimal = Decimal("1.0"),
) -> Decimal:
    """
    Calculate the estimated price for a visit (simplified interface).

    This is a convenience function for simple price calculations.
    For full breakdown, use RuleBasedPricingStrategy.calculate_price().

    Args:
        service_type: ServiceType instance with base_price and surge_multiplier
        distance_km: Distance to travel in kilometers
        time_of_day_multiplier: Time-based multiplier (default 1.0)

    Returns:
        Final price as Decimal.

    Note:
        For RTL compatibility, error messages should be in Arabic.
        This function uses the service_type.surge_multiplier field.
    """
    # Fetch per_km_rate from database via PricingFactor, with fallback to default
    strategy = RuleBasedPricingStrategy()
    per_km_rate = strategy.get_factor("per_km_rate")

    base = service_type.base_price
    distance_cost = distance_km * per_km_rate

    subtotal = base + distance_cost

    # Apply multipliers
    total = subtotal * service_type.surge_multiplier * time_of_day_multiplier

    return total.quantize(Decimal("0.01"))
