from decimal import Decimal
import pytest
from django.utils import timezone
from visits.services.pricing import RuleBasedPricingStrategy
from visits.models import PricingFactor


@pytest.mark.django_db
class TestPricingEnginePrecision:
    """Draconian tests ensuring absolutely zero floating point drift and exact mathematical algorithm mapping."""

    def setup_method(self):
        self.strategy = RuleBasedPricingStrategy()
        # Seed standard factors
        PricingFactor.objects.create(key="per_km_rate", value=Decimal("5.00"))
        PricingFactor.objects.create(key="day_multiplier", value=Decimal("1.00"))
        PricingFactor.objects.create(key="night_multiplier", value=Decimal("1.50"))
        PricingFactor.objects.create(key="night_start_hour", value=Decimal("22"))
        PricingFactor.objects.create(key="night_end_hour", value=Decimal("6"))

    def test_strict_formula_execution_daytime(self):
        """P = (B + D * R_km) * T * S_ai"""
        dt = timezone.now().replace(hour=12) # Day
        
        # B = 100.00, T = 1.00, D = 10.00, R_km = 5.00, S_ai = 1.50
        # P = (100.00 + (10.00 * 5.00)) * 1.00 * 1.50
        # P = (100.00 + 50.00) * 1.50 = 225.00
        res = self.strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("10.00"),
            request_time=dt,
            ai_surge_coefficient=Decimal("1.50")
        )
        
        assert res.final_price == Decimal("225.00")
        assert res.time_multiplier == Decimal("1.00")
        assert res.distance_fee == Decimal("50.00")

    def test_strict_formula_execution_nighttime(self):
        dt = timezone.now().replace(hour=2) # Night
        
        # B = 200.00, T = 1.50, D = 5.50, R_km = 5.00, S_ai = 1.00
        # P = (200.00 + (5.50 * 5.00)) * 1.50 * 1.00
        # P = (200.00 + 27.50) * 1.50 = 341.25
        res = self.strategy.calculate_price(
            base_price=Decimal("200.00"),
            distance_km=Decimal("5.50"),
            request_time=dt,
            # No ai_surge_coefficient provided, should default to 1.0
        )
        assert res.final_price == Decimal("341.25")

    def test_negative_base_price_raises_error(self):
        with pytest.raises(ValueError):
            self.strategy.calculate_price(
                base_price=Decimal("-10.00"),
                distance_km=Decimal("10.00"),
                request_time=timezone.now()
            )

    def test_negative_distance_raises_error(self):
        with pytest.raises(ValueError):
            self.strategy.calculate_price(
                base_price=Decimal("10.00"),
                distance_km=Decimal("-2.00"),
                request_time=timezone.now()
            )
