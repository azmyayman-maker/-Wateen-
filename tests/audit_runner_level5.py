
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Fix Path
PROJECT_ROOT = "d:/projects/Wateen"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- MOCKING HOSTILE ENVIRONMENT ---
sys.modules['django.contrib.gis'] = MagicMock()
sys.modules['django.contrib.gis.geos'] = MagicMock()
sys.modules['django.contrib.gis.db'] = MagicMock()
sys.modules['django.contrib.gis.db.models'] = MagicMock()
sys.modules['django_redis'] = MagicMock()
sys.modules['redis'] = MagicMock()

# Mock Point specifically as it's used in data structures
class MockPoint:
    def __init__(self, x=0, y=0, srid=4326):
        self.x = x
        self.y = y
        self.srid = srid

sys.modules['django.contrib.gis.geos'].Point = MockPoint

# Setup Django minimal settings for basic logic (timezone) if needed
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        TIME_ZONE='UTC',
        USE_TZ=True,
        # We DO NOT install 'visits' to prevent Django from trying to load models/apps
        # that might crash due to missing dependencies. We only need partial environment.
        INSTALLED_APPS=[], 
        SECRET_KEY='audit_test_key',
    )
    django.setup()

# Mock models that services might import
sys.modules['users.models'] = MagicMock()
sys.modules['visits.models'] = MagicMock()


# Import the code under test
from visits.services.pricing import RuleBasedPricingStrategy, PriceBreakdown
from visits.services.matching import GeoMatchingService

class TestLevel5Audit(unittest.TestCase):
    
    def setUp(self):
        self.cairo_tz = ZoneInfo("Africa/Cairo")

    # --- ARCHITECTURE & SAFETY CHECKS ---
    
    def test_pricing_timezone_strictness(self):
        """Verify that Night Shift logic strictly uses Cairo time."""
        strategy = RuleBasedPricingStrategy()
        
        # Mock database text factors
        strategy.get_factor = MagicMock(side_effect=lambda k: {
            "night_start_hour": Decimal("22"),
            "night_end_hour": Decimal("6"),
            "night_multiplier": Decimal("1.5"),
            "day_multiplier": Decimal("1.0")
        }.get(k, Decimal(0)))
        
        # Case 1: 9:00 PM UTC = 11:00 PM Cairo (Night Shift)
        # If code uses server time (UTC), 21 < 22 -> Day rate (WRONG)
        # If code uses Cairo time, 23 >= 22 -> Night rate (CORRECT)
        
        utc_time_9pm = datetime(2023, 1, 1, 21, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        is_night = strategy.is_night_hours(utc_time_9pm)
        
        # Only passes if conversion happens correctly
        self.assertTrue(is_night, "Architecture Halt: Pricing logic failed to convert UTC to Cairo time for night shift detection.")
        
    def test_redis_parsing_robustness(self):
        """Verify Matching Service does not crash on malformed data (Critical Defect Fix)."""
        service = GeoMatchingService()
        service._redis = MagicMock()
        service._is_available = MagicMock(return_value=True)
        
        # Mock GeoSearch return values
        # 1. Valid
        # 2. Malformed (no ID)
        # 3. Malformed (non-numeric ID)
        # 4. Bytes format
        mock_results = [
            (b'nurse:101', 1.5),
            ('nurse:invalid', 2.0),
            ('malformed_entry', 3.0),
            (b'nurse:102', 2.5)
        ]
        
        service._redis.geosearch.return_value = mock_results
        
        # Mock Database filter to return all IDs found (101, 102)
        # We need to mock the call to NurseProfile.objects.filter...
        # Since we mocked users.models above, we configure it:
        
        mock_qs = MagicMock()
        mock_qs.values_list.return_value = {101, 102}
        sys.modules['users.models'].NurseProfile.objects.filter.return_value = mock_qs
        
        # EXECUTE
        candidates = service.find_candidates(30.0, 31.0)
        
        # VALIDATE
        # Should contain 101 and 102.
        # Should NOT have crashed.
        
        ids = sorted([c['nurse_id'] for c in candidates])
        self.assertEqual(ids, [101, 102], "Parsing Error: Failed to extract valid IDs or correctly skip invalid ones.")
        
    def test_pricing_defaults_logging(self):
        """Verify that missing DB configurations trigger warning logs."""
        strategy = RuleBasedPricingStrategy()
        
        # We need to capture logging
        with self.assertLogs('visits.services.pricing', level='WARNING') as cm:
            # Force a lookup that fails DB (mocked inside get_factor import)
            # Since we globally mocked visits.models, PricingFactor.objects.get will need to raise DoesNotExist
            
            # We need to setup the specific mock for the import inside the method
            # Logic: `from visits.models import PricingFactor`
            # PricingFactor.DoesNotExist needs to be an Exception class
            
            class MockDoesNotExist(Exception): pass
            sys.modules['visits.models'].PricingFactor.DoesNotExist = MockDoesNotExist
            sys.modules['visits.models'].PricingFactor.objects.get.side_effect = MockDoesNotExist()
            
            val = strategy.get_factor("missing_key")
            
            # Check Result
            self.assertEqual(val, Decimal("0")) # Default fallback
            
            # Check Log
            self.assertTrue(any("Using default" in o for o in cm.output), "Security/Ops: Missing pricing factors must log warnings.")

    # --- NEGATIVE TESTING ---
    
    def test_matching_invalid_coordinates(self):
        """Verify defensive coding against invalid inputs."""
        service = GeoMatchingService()
        
        # Lat > 90
        with self.assertRaises(ValueError):
            service.find_candidates(91.0, 30.0)
            
    def test_pricing_zero_distance(self):
        """Verify math safety."""
        strategy = RuleBasedPricingStrategy()
        
        # Correct mock:
        def factor_side_effect(k):
             defaults = {
                 "per_km_rate": Decimal("10"),
                 "day_multiplier": Decimal("1.0"),
                 "night_multiplier": Decimal("1.5"),
                 "night_start_hour": Decimal("22"),
                 "night_end_hour": Decimal("6"),
             }
             return defaults.get(k, Decimal("0"))
             
        strategy.get_factor = MagicMock(side_effect=factor_side_effect)
        
        # 0 distance
        breakdown = strategy.calculate_price(Decimal("100"), Decimal("0"))
        
        self.assertEqual(breakdown.distance_fee, Decimal("0.00"))
        self.assertEqual(breakdown.final_price, Decimal("100.00"))


if __name__ == '__main__':
    unittest.main()
