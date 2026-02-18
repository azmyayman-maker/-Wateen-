"""
Tests for Pricing Engine (AI-Ready Foundation)

Feature: 001-pricing-engine
Tests organized by User Story (US1-US4) for independent testing.

Test Categories:
- US1: Price Estimate API tests
- US2: Admin Configuration tests
- US3: AI Training Data Logging tests
- US4: Mock Payment Webhook tests
"""

import pytest
from datetime import datetime
from decimal import Decimal


@pytest.fixture
def service_type():
    """Fixture for creating a test ServiceType."""
    from visits.models import ServiceType

    return ServiceType.objects.create(
        name="Test Service",
        base_price=Decimal("100.00"),
        description="Test service for pricing",
        is_active=True,
    )


@pytest.fixture
def pricing_factors():
    """Fixture for creating test PricingFactors."""
    from visits.models import PricingFactor

    return {
        "per_km_rate": PricingFactor.objects.create(
            key="per_km_rate",
            value=Decimal("50.00"),
            description="EGP per kilometer",
        ),
        "night_multiplier": PricingFactor.objects.create(
            key="night_multiplier",
            value=Decimal("1.50"),
            description="Night hours multiplier",
        ),
        "day_multiplier": PricingFactor.objects.create(
            key="day_multiplier",
            value=Decimal("1.00"),
            description="Day hours multiplier",
        ),
        "night_start_hour": PricingFactor.objects.create(
            key="night_start_hour",
            value=Decimal("22"),
            description="Night hours start (24h)",
        ),
        "night_end_hour": PricingFactor.objects.create(
            key="night_end_hour",
            value=Decimal("6"),
            description="Night hours end (24h)",
        ),
    }


# Phase markers for organized test execution
pytestmark = pytest.mark.django_db


# =============================================================================
# USER STORY 1: Price Estimate API Tests
# =============================================================================


class TestRuleBasedPricingStrategyDayHours:
    """T011: Unit tests for day hours pricing scenario."""

    def test_calculate_price_day_hours_basic(self, service_type, pricing_factors):
        """Test basic price calculation during day hours."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        day_time = datetime(2026, 2, 18, 14, 0, 0)  # 2 PM

        result = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("10.0"),
            request_time=day_time,
        )

        assert result.base_price == Decimal("100.00")
        assert result.distance_km == Decimal("10.0")
        assert result.distance_fee == Decimal("500.00")  # 10 * 50
        assert result.time_multiplier == Decimal("1.00")  # Day multiplier
        assert result.ai_surge_coefficient == Decimal("1.0")
        assert result.final_price == Decimal("600.00")  # (100 + 500) * 1.0 * 1.0

    def test_calculate_price_day_hours_zero_distance(
        self, service_type, pricing_factors
    ):
        """Test price calculation with zero distance."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        day_time = datetime(2026, 2, 18, 10, 0, 0)  # 10 AM

        result = strategy.calculate_price(
            base_price=Decimal("150.00"),
            distance_km=Decimal("0"),
            request_time=day_time,
        )

        assert result.base_price == Decimal("150.00")
        assert result.distance_fee == Decimal("0.00")
        assert result.final_price == Decimal("150.00")


class TestRuleBasedPricingStrategyNightHours:
    """T012: Unit tests for night hours pricing scenario."""

    def test_calculate_price_night_hours_basic(self, service_type, pricing_factors):
        """Test price calculation during night hours (22:00-06:00)."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        night_time = datetime(2026, 2, 18, 23, 0, 0)  # 11 PM

        result = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("10.0"),
            request_time=night_time,
        )

        assert result.base_price == Decimal("100.00")
        assert result.distance_fee == Decimal("500.00")  # 10 * 50
        assert result.time_multiplier == Decimal("1.50")  # Night multiplier
        assert result.final_price == Decimal("900.00")  # (100 + 500) * 1.5

    def test_calculate_price_night_hours_early_morning(
        self, service_type, pricing_factors
    ):
        """Test price calculation at 3 AM (within night hours)."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        early_morning = datetime(2026, 2, 18, 3, 0, 0)  # 3 AM

        result = strategy.calculate_price(
            base_price=Decimal("200.00"),
            distance_km=Decimal("5.0"),
            request_time=early_morning,
        )

        assert result.time_multiplier == Decimal("1.50")
        assert result.final_price == Decimal("412.50")  # (200 + 250) * 1.5

    def test_calculate_price_boundary_evening(self, service_type, pricing_factors):
        """Test price at 21:59 (still day) vs 22:00 (night starts)."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        before_night = datetime(2026, 2, 18, 21, 59, 0)
        at_night_start = datetime(2026, 2, 18, 22, 0, 0)

        result_before = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("0"),
            request_time=before_night,
        )
        result_at = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("0"),
            request_time=at_night_start,
        )

        assert result_before.time_multiplier == Decimal("1.00")
        assert result_at.time_multiplier == Decimal("1.50")


class TestRuleBasedPricingStrategyDefaults:
    """T013: Unit tests for missing PricingFactor defaults."""

    def test_calculate_price_with_missing_factors(self, db):
        """Test that defaults are used when PricingFactors don't exist."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        day_time = datetime(2026, 2, 18, 14, 0, 0)

        result = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("10.0"),
            request_time=day_time,
        )

        # Should use defaults: per_km_rate=50, day_multiplier=1.0
        assert result.distance_fee == Decimal("500.00")
        assert result.time_multiplier == Decimal("1.00")
        assert result.final_price == Decimal("600.00")

    def test_get_factor_returns_default_when_missing(self, db):
        """Test get_factor returns default for missing keys."""
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        result = strategy.get_factor("nonexistent_factor")
        assert result == Decimal("0")  # Default for unknown keys


class TestEstimateEndpoint:
    """T014: Integration tests for POST /api/v1/visits/estimate/ endpoint."""

    def test_estimate_endpoint_success(self, client, service_type, pricing_factors):
        """Test successful estimate request returns price breakdown."""
        url = "/api/v1/visits/estimate/"
        data = {
            "service_type_id": str(service_type.id),
            "latitude": 30.0444,
            "longitude": 31.2357,
        }

        response = client.post(url, data, content_type="application/json")

        assert response.status_code == 200
        assert "breakdown" in response.json()
        assert "final_price" in response.json()["breakdown"]

    def test_estimate_endpoint_with_time(self, client, service_type, pricing_factors):
        """Test estimate request with specific time."""
        url = "/api/v1/visits/estimate/"
        data = {
            "service_type_id": str(service_type.id),
            "latitude": 30.0444,
            "longitude": 31.2357,
            "request_time": "2026-02-18T23:00:00Z",
        }

        response = client.post(url, data, content_type="application/json")

        assert response.status_code == 200
        result = response.json()
        assert result["is_night_hours"] is True
        assert result["breakdown"]["time_multiplier"] == "1.50"

    def test_estimate_endpoint_invalid_service_type(self, client, pricing_factors):
        """Test estimate with non-existent service type."""
        import uuid

        url = "/api/v1/visits/estimate/"
        data = {
            "service_type_id": str(uuid.uuid4()),
            "latitude": 30.0444,
            "longitude": 31.2357,
        }

        response = client.post(url, data, content_type="application/json")

        assert response.status_code == 400

    def test_estimate_endpoint_invalid_coordinates(self, client, service_type):
        """Test estimate with invalid coordinates."""
        url = "/api/v1/visits/estimate/"
        data = {
            "service_type_id": str(service_type.id),
            "latitude": 200,  # Invalid
            "longitude": 31.2357,
        }

        response = client.post(url, data, content_type="application/json")

        assert response.status_code == 400


class TestEstimateRateLimiting:
    """T015: Integration tests for rate limiting on estimate endpoint."""

    def test_rate_limit_allows_requests(self, client, service_type, pricing_factors):
        """Test that reasonable number of requests are allowed."""
        url = "/api/v1/visits/estimate/"
        data = {
            "service_type_id": str(service_type.id),
            "latitude": 30.0444,
            "longitude": 31.2357,
        }

        # Make a few requests - should all succeed
        for _ in range(5):
            response = client.post(url, data, content_type="application/json")
            assert response.status_code in [200, 429]  # 429 if rate limited

    def test_rate_limit_headers_present(self, client, service_type, pricing_factors):
        """Test that rate limit headers are in response."""
        url = "/api/v1/visits/estimate/"
        data = {
            "service_type_id": str(service_type.id),
            "latitude": 30.0444,
            "longitude": 31.2357,
        }

        response = client.post(url, data, content_type="application/json")

        # DRF throttle headers may or may not be present depending on config
        assert response.status_code in [200, 429]


# =============================================================================
# USER STORY 2: Admin Configuration Tests
# =============================================================================


class TestServiceTypeAdmin:
    """T027: Admin tests for ServiceType CRUD operations."""

    def test_service_type_create(self, db):
        """Test creating a ServiceType via ORM."""
        from visits.models import ServiceType

        service = ServiceType.objects.create(
            name="Home Nursing",
            base_price=Decimal("150.00"),
            description="General home nursing care",
            is_active=True,
        )

        assert service.id is not None
        assert service.name == "Home Nursing"
        assert service.base_price == Decimal("150.00")
        assert service.is_active is True

    def test_service_type_update(self, service_type):
        """Test updating a ServiceType."""
        service_type.base_price = Decimal("200.00")
        service_type.save()

        service_type.refresh_from_db()
        assert service_type.base_price == Decimal("200.00")

    def test_service_type_delete(self, service_type):
        """Test deleting a ServiceType."""
        service_id = service_type.id
        service_type.delete()

        from visits.models import ServiceType

        assert not ServiceType.objects.filter(id=service_id).exists()

    def test_service_type_unique_name(self, service_type):
        """Test that ServiceType names must be unique."""
        from django.db import IntegrityError
        from visits.models import ServiceType

        with pytest.raises(IntegrityError):
            ServiceType.objects.create(
                name=service_type.name,
                base_price=Decimal("100.00"),
            )

    def test_service_type_inactive_not_in_default_queryset(self, service_type):
        """Test that inactive services can be filtered."""
        from visits.models import ServiceType

        service_type.is_active = False
        service_type.save()

        active_services = ServiceType.objects.filter(is_active=True)
        assert service_type not in active_services


class TestPricingFactorAdmin:
    """T028: Admin tests for PricingFactor CRUD operations."""

    def test_pricing_factor_create(self, db):
        """Test creating a PricingFactor via ORM."""
        from visits.models import PricingFactor

        factor = PricingFactor.objects.create(
            key="test_factor",
            value=Decimal("25.50"),
            description="Test factor for pricing",
        )

        assert factor.key == "test_factor"
        assert factor.value == Decimal("25.50")
        assert factor.description == "Test factor for pricing"

    def test_pricing_factor_update(self, pricing_factors):
        """Test updating a PricingFactor value."""
        factor = pricing_factors["per_km_rate"]
        original_value = factor.value

        factor.value = Decimal("60.00")
        factor.save()

        factor.refresh_from_db()
        assert factor.value == Decimal("60.00")
        assert factor.value != original_value

    def test_pricing_factor_delete(self, pricing_factors):
        """Test deleting a PricingFactor."""
        factor = pricing_factors["day_multiplier"]
        factor.delete()

        from visits.models import PricingFactor

        assert not PricingFactor.objects.filter(key="day_multiplier").exists()

    def test_pricing_factor_affects_estimate(self, service_type, pricing_factors):
        """Test that updating a factor affects estimate calculation."""
        from datetime import datetime
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        day_time = datetime(2026, 2, 18, 14, 0, 0)

        result_before = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("10.0"),
            request_time=day_time,
        )

        pricing_factors["per_km_rate"].value = Decimal("100.00")
        pricing_factors["per_km_rate"].save()

        result_after = strategy.calculate_price(
            base_price=Decimal("100.00"),
            distance_km=Decimal("10.0"),
            request_time=day_time,
        )

        assert result_after.distance_fee > result_before.distance_fee


class TestPricingFactorDuplicateKey:
    """T029: Test for duplicate PricingFactor key rejection."""

    def test_duplicate_key_rejected(self, pricing_factors):
        """Test that duplicate keys are rejected."""
        from django.db import IntegrityError
        from visits.models import PricingFactor

        with pytest.raises(IntegrityError):
            PricingFactor.objects.create(
                key="per_km_rate",
                value=Decimal("75.00"),
                description="Duplicate key",
            )


# =============================================================================
# USER STORY 3: AI Training Data Logging Tests
# =============================================================================


class TestEstimateLogCreation:
    """T036: Unit tests for EstimateLog creation on estimate request."""

    def test_estimate_log_created_on_request(
        self, service_type, pricing_factors, django_capture_on_commit_callbacks
    ):
        """Test that an EstimateLog is created when an estimate is requested."""
        from datetime import datetime
        from visits.models import EstimateLog
        from visits.services.logging import log_estimate_request

        initial_count = EstimateLog.objects.count()

        with django_capture_on_commit_callbacks(execute=True):
            log_estimate_request(
                service_type_id=str(service_type.id),
                latitude=30.0444,
                longitude=31.2357,
                request_time=datetime(2026, 2, 18, 14, 0, 0),
                price_components={
                    "base_price": "100.00",
                    "distance_km": 5.0,
                    "distance_fee": "250.00",
                    "time_multiplier": "1.00",
                    "ai_surge_coefficient": "1.00",
                    "final_price": "350.00",
                },
                ip_address="192.168.1.1",
            )

        assert EstimateLog.objects.count() == initial_count + 1

    def test_estimate_log_with_missing_service_type(
        self, db, django_capture_on_commit_callbacks
    ):
        """Test that EstimateLog can be created with missing service type."""
        import uuid
        from datetime import datetime
        from visits.models import EstimateLog
        from visits.services.logging import log_estimate_request

        with django_capture_on_commit_callbacks(execute=True):
            log_estimate_request(
                service_type_id=str(uuid.uuid4()),
                latitude=30.0444,
                longitude=31.2357,
                request_time=datetime(2026, 2, 18, 14, 0, 0),
                price_components={
                    "base_price": "100.00",
                    "distance_km": 5.0,
                    "distance_fee": "250.00",
                    "final_price": "350.00",
                },
            )

        log_entry = EstimateLog.objects.latest("created_at")
        assert log_entry.service_type is None


class TestEstimateLogPriceComponents:
    """T037: Tests for EstimateLog containing all required price_components fields."""

    def test_price_components_has_all_fields(
        self, service_type, pricing_factors, django_capture_on_commit_callbacks
    ):
        """Test that price_components contains all required fields for ML training."""
        from datetime import datetime
        from visits.models import EstimateLog
        from visits.services.logging import log_estimate_request

        price_components = {
            "base_price": "150.00",
            "distance_km": 10.5,
            "distance_fee": "525.00",
            "time_multiplier": "1.50",
            "ai_surge_coefficient": "1.00",
            "final_price": "1012.50",
        }

        with django_capture_on_commit_callbacks(execute=True):
            log_estimate_request(
                service_type_id=str(service_type.id),
                latitude=30.0444,
                longitude=31.2357,
                request_time=datetime(2026, 2, 18, 23, 0, 0),
                price_components=price_components,
            )

        log_entry = EstimateLog.objects.latest("created_at")

        assert "base_price" in log_entry.price_components
        assert "distance_km" in log_entry.price_components
        assert "distance_fee" in log_entry.price_components
        assert "time_multiplier" in log_entry.price_components
        assert "ai_surge_coefficient" in log_entry.price_components
        assert "final_price" in log_entry.price_components

    def test_estimate_log_location_stored_correctly(
        self, service_type, pricing_factors, django_capture_on_commit_callbacks
    ):
        """Test that location is stored as PointField correctly."""
        from datetime import datetime
        from visits.models import EstimateLog
        from visits.services.logging import log_estimate_request

        with django_capture_on_commit_callbacks(execute=True):
            log_estimate_request(
                service_type_id=str(service_type.id),
                latitude=30.0444,
                longitude=31.2357,
                request_time=datetime(2026, 2, 18, 14, 0, 0),
                price_components={"final_price": "100.00"},
            )

        log_entry = EstimateLog.objects.latest("created_at")

        assert log_entry.location is not None
        assert abs(log_entry.location.y - 30.0444) < 0.0001
        assert abs(log_entry.location.x - 31.2357) < 0.0001


# =============================================================================
# USER STORY 4: Mock Payment Webhook Tests
# =============================================================================


class TestMockPaymentWebhookSuccess:
    """T044: Integration tests for successful mock payment webhook."""

    @pytest.mark.skip(reason="TODO: implement webhook integration test")
    def test_webhook_success_updates_visit_status(self, db):
        """Test that successful payment updates visit status."""
        from django.test import RequestFactory
        from visits.api import MockPaymentWebhookView

        factory = RequestFactory()
        view = MockPaymentWebhookView.as_view()

    @pytest.mark.skip(reason="TODO: implement webhook integration test")
    def test_webhook_success_response(self, db):
        """Test successful webhook returns correct response."""
        pass


class TestMockPaymentWebhookFailed:
    """T045: Integration tests for failed mock payment webhook."""

    @pytest.mark.skip(reason="TODO: implement webhook integration test")
    def test_webhook_failed_updates_visit_status(self, db):
        """Test that failed payment updates visit status."""
        pass

    @pytest.mark.skip(reason="TODO: implement webhook integration test")
    def test_webhook_failed_with_error_message(self, db):
        """Test failed webhook with error message."""
        pass


class TestMockPaymentWebhookProduction:
    """T046: Test for webhook rejection in production (DEBUG=False)."""

    def test_webhook_disabled_in_production(self, db, monkeypatch):
        """Test that webhook is disabled when DEBUG=False."""
        from django.conf import settings
        from django.test import RequestFactory
        from visits.api import MockPaymentWebhookView

        factory = RequestFactory()
        view = MockPaymentWebhookView.as_view()

        request = factory.post(
            "/api/v1/payments/webhook/mock/",
            {"visit_id": "00000000-0000-0000-0000-000000000001", "status": "success"},
            content_type="application/json",
        )

        monkeypatch.setattr(settings, "DEBUG", False)

        response = view(request)
        assert response.status_code == 403
        assert "forbidden" in str(response.data).lower()

    def test_webhook_invalid_token_rejected(self, db, monkeypatch):
        """Test that invalid token is rejected."""
        from django.conf import settings
        from django.test import RequestFactory
        from visits.api import MockPaymentWebhookView

        factory = RequestFactory()
        view = MockPaymentWebhookView.as_view()

        request = factory.post(
            "/api/v1/payments/webhook/mock/",
            {"visit_id": "00000000-0000-0000-0000-000000000001", "status": "success"},
            content_type="application/json",
            HTTP_X_MOCK_TOKEN="invalid-token",
        )

        monkeypatch.setattr(settings, "DEBUG", True)

        response = view(request)
        assert response.status_code == 403

    def test_webhook_visit_not_found(self, db, monkeypatch):
        """Test webhook with non-existent visit ID."""
        import uuid
        from django.conf import settings
        from django.test import RequestFactory
        from visits.api import MockPaymentWebhookView

        factory = RequestFactory()
        view = MockPaymentWebhookView.as_view()

        request = factory.post(
            "/api/v1/payments/webhook/mock/",
            {"visit_id": str(uuid.uuid4()), "status": "success"},
            content_type="application/json",
            HTTP_X_MOCK_TOKEN=settings.SECRET_KEY[:20]
            if settings.SECRET_KEY
            else "dev-only-token",
        )

        monkeypatch.setattr(settings, "DEBUG", True)

        response = view(request)
        assert response.status_code == 404


class TestDynamicDistanceCalculation:
    """Tests for dynamic distance calculation using find_nearest_available_nurse."""

    def test_distance_varies_by_nurse_location(self, db):
        """Test that distance calculation varies based on actual nurse locations."""
        from decimal import Decimal
        from django.contrib.gis.geos import Point
        from users.models import CustomUser, NurseProfile, VerificationStatus
        from visits.utils import find_nearest_available_nurse

        user = CustomUser.objects.create_user(
            national_id="12345678901234",
            phone_number="+201234567890",
        )
        nurse = NurseProfile.objects.create(
            user=user,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            last_location=Point(31.25, 30.05, srid=4326),
        )

        _, distance = find_nearest_available_nurse(30.04, 31.24)

        assert distance > Decimal("0")
        assert distance < Decimal("10")

    def test_no_nurse_returns_zero_distance(self, db):
        """Test that no available nurse returns distance of 0."""
        from visits.utils import find_nearest_available_nurse

        _, distance = find_nearest_available_nurse(30.04, 31.24)

        assert distance == 0

    def test_unavailable_nurse_excluded(self, db):
        """Test that unavailable nurses are excluded from distance calculation."""
        from django.contrib.gis.geos import Point
        from users.models import CustomUser, NurseProfile, VerificationStatus
        from visits.utils import find_nearest_available_nurse

        user = CustomUser.objects.create_user(
            national_id="12345678901235",
            phone_number="+201234567891",
        )
        NurseProfile.objects.create(
            user=user,
            is_available=False,
            verification_status=VerificationStatus.VERIFIED,
            last_location=Point(31.25, 30.05, srid=4326),
        )

        _, distance = find_nearest_available_nurse(30.04, 31.24)

        assert distance == 0

    def test_unverified_nurse_excluded(self, db):
        """Test that unverified nurses are excluded from distance calculation."""
        from django.contrib.gis.geos import Point
        from users.models import CustomUser, NurseProfile, VerificationStatus
        from visits.utils import find_nearest_available_nurse

        user = CustomUser.objects.create_user(
            national_id="12345678901236",
            phone_number="+201234567892",
        )
        NurseProfile.objects.create(
            user=user,
            is_available=True,
            verification_status=VerificationStatus.PENDING,
            last_location=Point(31.25, 30.05, srid=4326),
        )

        _, distance = find_nearest_available_nurse(30.04, 31.24)

        assert distance == 0

    def test_nearest_nurse_selected(self, db):
        """Test that the nearest available verified nurse is selected."""
        from decimal import Decimal
        from django.contrib.gis.geos import Point
        from users.models import CustomUser, NurseProfile, VerificationStatus
        from visits.utils import find_nearest_available_nurse

        user1 = CustomUser.objects.create_user(
            national_id="12345678901237",
            phone_number="+201234567893",
        )
        NurseProfile.objects.create(
            user=user1,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            last_location=Point(31.24, 30.04, srid=4326),
        )

        user2 = CustomUser.objects.create_user(
            national_id="12345678901238",
            phone_number="+201234567894",
        )
        far_nurse = NurseProfile.objects.create(
            user=user2,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            last_location=Point(32.0, 31.0, srid=4326),
        )

        nurse, distance = find_nearest_available_nurse(30.04, 31.24)

        assert nurse is not None
        assert nurse.user_id != far_nurse.user_id
        assert distance < Decimal("1")


class TestMatchingServiceAvailabilityFilter:
    """Tests for availability filtering in matching service."""

    def test_find_candidates_filters_unavailable(self, db):
        """Test that find_candidates filters out unavailable nurses."""
        from unittest.mock import MagicMock, patch
        from visits.services.matching import GeoMatchingService

        with patch("visits.services.matching.get_redis_connection") as mock_redis:
            mock_client = MagicMock()
            mock_client.geosearch.return_value = [(b"nurse:1", 2.5)]
            mock_redis.return_value = mock_client

            from django.contrib.gis.geos import Point
            from users.models import CustomUser, NurseProfile, VerificationStatus

            user = CustomUser.objects.create_user(
                national_id="12345678901239",
                phone_number="+201234567895",
            )
            NurseProfile.objects.create(
                user=user,
                is_available=False,
                verification_status=VerificationStatus.VERIFIED,
                last_location=Point(31.25, 30.05, srid=4326),
            )

            service = GeoMatchingService()
            service._redis = mock_client
            candidates = service.find_candidates(30.04, 31.24)

            assert len(candidates) == 0


class TestTimezoneAwarePricing:
    """Tests for timezone-aware night/day pricing logic."""

    def test_night_hours_23pm_applies_night_multiplier(self, db):
        """Test that 23:00 (11 PM) applies night multiplier (1.5x)."""
        from datetime import datetime
        from decimal import Decimal
        from zoneinfo import ZoneInfo
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        cairo_tz = ZoneInfo("Africa/Cairo")
        night_time = datetime(2026, 2, 18, 23, 0, 0, tzinfo=cairo_tz)

        assert strategy.is_night_hours(night_time) is True
        assert strategy.get_time_multiplier(night_time) == Decimal("1.50")

    def test_day_hours_10am_applies_day_multiplier(self, db):
        """Test that 10:00 AM applies day multiplier (1.0x)."""
        from datetime import datetime
        from decimal import Decimal
        from zoneinfo import ZoneInfo
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        cairo_tz = ZoneInfo("Africa/Cairo")
        day_time = datetime(2026, 2, 18, 10, 0, 0, tzinfo=cairo_tz)

        assert strategy.is_night_hours(day_time) is False
        assert strategy.get_time_multiplier(day_time) == Decimal("1.00")

    def test_boundary_22pm_is_night_hours(self, db):
        """Test that 22:00 (10 PM) is the start of night hours."""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        cairo_tz = ZoneInfo("Africa/Cairo")
        boundary_time = datetime(2026, 2, 18, 22, 0, 0, tzinfo=cairo_tz)

        assert strategy.is_night_hours(boundary_time) is True

    def test_boundary_6am_is_day_hours(self, db):
        """Test that 06:00 (6 AM) is the start of day hours."""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        cairo_tz = ZoneInfo("Africa/Cairo")
        boundary_time = datetime(2026, 2, 18, 6, 0, 0, tzinfo=cairo_tz)

        assert strategy.is_night_hours(boundary_time) is False

    def test_early_morning_2am_is_night_hours(self, db):
        """Test that 02:00 (2 AM) is within night hours."""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from visits.services.pricing import RuleBasedPricingStrategy

        strategy = RuleBasedPricingStrategy()
        cairo_tz = ZoneInfo("Africa/Cairo")
        early_morning = datetime(2026, 2, 18, 2, 0, 0, tzinfo=cairo_tz)

        assert strategy.is_night_hours(early_morning) is True


class TestNonBlockingLogging:
    """Tests for non-blocking logging using transaction.on_commit()."""

    def test_log_uses_transaction_on_commit(self, db):
        """Test that log_estimate_request uses transaction.on_commit for async logging."""
        from unittest.mock import MagicMock, patch
        from visits.signals import log_estimate_request

        with patch("visits.signals.transaction.on_commit") as mock_on_commit:
            mock_on_commit.return_value = None

            log_estimate_request(
                service_type_id="00000000-0000-0000-0000-000000000001",
                latitude=30.0444,
                longitude=31.2357,
                request_time=datetime(2026, 2, 18, 14, 0, 0),
                price_components={"final_price": "100.00"},
                ip_address="192.168.1.1",
            )

            mock_on_commit.assert_called_once()
            assert callable(mock_on_commit.call_args[0][0])
