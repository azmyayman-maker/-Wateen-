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
from typing import Optional

from django.utils.translation import gettext_lazy as _


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
        except Exception:
            pass

        return self.DEFAULTS.get(key, Decimal("0"))

    def _is_night_hours(self, request_time: datetime) -> bool:
        """
        Check if the given time falls within night hours.

        Night hours are defined as 22:00 to 06:00.

        Args:
            request_time: The datetime to check

        Returns:
            True if within night hours, False otherwise.
        """
        night_start = int(self.get_factor("night_start_hour"))
        night_end = int(self.get_factor("night_end_hour"))

        hour = request_time.hour

        # Night hours span midnight (e.g., 22:00 to 06:00)
        if night_start > night_end:
            return hour >= night_start or hour < night_end
        else:
            return night_start <= hour < night_end

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
        # Get pricing factors
        per_km_rate = self.get_factor("per_km_rate")

        # Determine time multiplier based on day/night
        if self._is_night_hours(request_time):
            time_multiplier = self.get_factor("night_multiplier")
        else:
            time_multiplier = self.get_factor("day_multiplier")

        # Calculate distance fee
        distance_fee = (distance_km * per_km_rate).quantize(Decimal("0.01"))

        # AI surge coefficient (placeholder for ML model)
        if ai_surge_coefficient is None:
            ai_surge_coefficient = Decimal("1.0")

        # Calculate final price
        subtotal = base_price + distance_fee
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
    # Placeholder for a configurable rate. In a real app, this comes from PricingFactor.
    PER_KM_RATE = Decimal("5.0")

    base = service_type.base_price
    distance_cost = distance_km * PER_KM_RATE

    subtotal = base + distance_cost

    # Apply multipliers
    total = subtotal * service_type.surge_multiplier * time_of_day_multiplier

    return total.quantize(Decimal("0.01"))
