"""
Tests for the GeoMatchingService.
Uses fakeredis to provide an in-memory Redis instance for testing
geospatial operations without requiring a running Redis server.
"""

import pytest
from unittest.mock import patch
import fakeredis
import redis
from visits.services.matching import GeoMatchingService


@pytest.fixture
def fake_redis():
    """Create a fakeredis instance for testing."""
    server = fakeredis.FakeServer()
    return fakeredis.FakeRedis(server=server)


@pytest.fixture
def geo_service(fake_redis):
    """Create a GeoMatchingService with a mocked Redis connection."""
    with patch(
        "visits.services.matching.get_redis_connection", return_value=fake_redis
    ):
        service = GeoMatchingService()
    return service


class TestCoordinateValidation:
    """Tests for coordinate validation."""

    def test_invalid_latitude_raises_error(self, geo_service):
        with pytest.raises(ValueError, match="Invalid latitude"):
            geo_service.update_nurse_location(1, 91.0, 30.0)

    def test_invalid_latitude_below_range(self, geo_service):
        with pytest.raises(ValueError, match="Invalid latitude"):
            geo_service.update_nurse_location(1, -91.0, 30.0)

    def test_invalid_longitude_raises_error(self, geo_service):
        with pytest.raises(ValueError, match="Invalid longitude"):
            geo_service.find_candidates(30.0, 181.0)

    def test_invalid_longitude_below_range(self, geo_service):
        with pytest.raises(ValueError, match="Invalid longitude"):
            geo_service.find_candidates(30.0, -181.0)

    def test_negative_boundary_values_are_valid(self, geo_service):
        result = geo_service.update_nurse_location(1, -90.0, -180.0)
        assert result is True

    def test_positive_boundary_values_are_valid(self, geo_service):
        result = geo_service.update_nurse_location(2, 90.0, 180.0)
        assert result is True

    def test_zero_coordinates_are_valid(self, geo_service):
        result = geo_service.update_nurse_location(3, 0.0, 0.0)
        assert result is True


class TestUpdateNurseLocation:
    """Tests for GeoMatchingService.update_nurse_location()."""

    def test_update_location_returns_true(self, geo_service):
        result = geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        assert result is True

    def test_update_location_stores_coordinates(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        location = geo_service.get_nurse_location(nurse_id=1)
        assert location is not None
        lat, lng = location
        assert abs(lat - 30.0444) < 0.001
        assert abs(lng - 31.2357) < 0.001

    def test_update_location_overwrites_previous(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0000, lng=31.0000)
        geo_service.update_nurse_location(nurse_id=1, lat=30.1000, lng=31.1000)
        location = geo_service.get_nurse_location(nurse_id=1)
        assert location is not None
        lat, lng = location
        assert abs(lat - 30.1000) < 0.001
        assert abs(lng - 31.1000) < 0.001


class TestFindCandidates:
    """Tests for GeoMatchingService.find_candidates()."""

    def test_nurse_within_radius_is_found(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        candidates = geo_service.find_candidates(
            patient_lat=30.0450, patient_lng=31.2360, radius_km=5.0
        )
        assert len(candidates) == 1
        assert candidates[0]["nurse_id"] == 1
        assert candidates[0]["distance_km"] < 5.0

    def test_nurse_outside_radius_not_found(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=31.0000, lng=32.0000)
        candidates = geo_service.find_candidates(
            patient_lat=30.0444, patient_lng=31.2357, radius_km=5.0
        )
        assert len(candidates) == 0

    def test_multiple_nurses_sorted_by_distance(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0445, lng=31.2358)
        geo_service.update_nurse_location(nurse_id=2, lat=30.0500, lng=31.2400)
        geo_service.update_nurse_location(nurse_id=3, lat=31.0000, lng=32.0000)

        candidates = geo_service.find_candidates(
            patient_lat=30.0444, patient_lng=31.2357, radius_km=5.0
        )
        assert len(candidates) == 2
        assert candidates[0]["nurse_id"] == 1
        assert candidates[1]["nurse_id"] == 2
        assert candidates[0]["distance_km"] <= candidates[1]["distance_km"]

    def test_empty_index_returns_empty_list(self, geo_service):
        candidates = geo_service.find_candidates(
            patient_lat=30.0444, patient_lng=31.2357, radius_km=5.0
        )
        assert candidates == []


class TestGetNurseLocation:
    """Tests for GeoMatchingService.get_nurse_location()."""

    def test_returns_coordinates_for_known_nurse(self, geo_service):
        geo_service.update_nurse_location(nurse_id=42, lat=30.0444, lng=31.2357)
        location = geo_service.get_nurse_location(nurse_id=42)
        assert location is not None
        lat, lng = location
        assert abs(lat - 30.0444) < 0.001
        assert abs(lng - 31.2357) < 0.001

    def test_returns_none_for_unknown_nurse(self, geo_service):
        location = geo_service.get_nurse_location(nurse_id=999)
        assert location is None


class TestRemoveNurse:
    """Tests for GeoMatchingService.remove_nurse()."""

    def test_remove_existing_nurse(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        result = geo_service.remove_nurse(nurse_id=1)
        assert result is True
        assert geo_service.get_nurse_location(nurse_id=1) is None

    def test_remove_nonexistent_nurse_returns_false(self, geo_service):
        result = geo_service.remove_nurse(nurse_id=999)
        assert result is False


class TestRedisErrorHandling:
    """Tests for graceful Redis error handling."""

    def test_init_handles_redis_error(self):
        with patch(
            "visits.services.matching.get_redis_connection",
            side_effect=redis.RedisError("Connection refused"),
        ):
            service = GeoMatchingService()
        assert service._redis is None
        assert service.update_nurse_location(1, 30.0, 31.0) is False

    def test_update_returns_false_when_redis_unavailable(self):
        with patch(
            "visits.services.matching.get_redis_connection",
            side_effect=redis.RedisError("Connection refused"),
        ):
            service = GeoMatchingService()
        result = service.update_nurse_location(nurse_id=1, lat=30.0, lng=31.0)
        assert result is False

    def test_find_returns_empty_when_redis_unavailable(self):
        with patch(
            "visits.services.matching.get_redis_connection",
            side_effect=redis.RedisError("Connection refused"),
        ):
            service = GeoMatchingService()
        result = service.find_candidates(patient_lat=30.0, patient_lng=31.0)
        assert result == []

    def test_get_location_returns_none_when_redis_unavailable(self):
        with patch(
            "visits.services.matching.get_redis_connection",
            side_effect=redis.RedisError("Connection refused"),
        ):
            service = GeoMatchingService()
        result = service.get_nurse_location(nurse_id=1)
        assert result is None

    def test_remove_returns_false_when_redis_unavailable(self):
        with patch(
            "visits.services.matching.get_redis_connection",
            side_effect=redis.RedisError("Connection refused"),
        ):
            service = GeoMatchingService()
        result = service.remove_nurse(nurse_id=1)
        assert result is False

    def test_redis_error_during_update_returns_false(self, geo_service):
        with patch.object(
            geo_service._redis,
            "geoadd",
            side_effect=redis.RedisError("Connection lost"),
        ):
            result = geo_service.update_nurse_location(1, 30.0, 31.0)
            assert result is False

    def test_redis_error_during_find_returns_empty(self, geo_service):
        with patch.object(
            geo_service._redis,
            "geosearch",
            side_effect=redis.RedisError("Connection lost"),
        ):
            result = geo_service.find_candidates(30.0, 31.0)
            assert result == []

    def test_redis_error_during_get_location_returns_none(self, geo_service):
        with patch.object(
            geo_service._redis,
            "geopos",
            side_effect=redis.RedisError("Connection lost"),
        ):
            result = geo_service.get_nurse_location(1)
            assert result is None

    def test_redis_error_during_remove_returns_false(self, geo_service):
        with patch.object(
            geo_service._redis, "zrem", side_effect=redis.RedisError("Connection lost")
        ):
            result = geo_service.remove_nurse(1)
            assert result is False
