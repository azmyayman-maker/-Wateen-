from unittest.mock import MagicMock, patch

from django.test import TestCase

from visits.services.matching import GeoMatchingService


class TestGeoMatchingDecoding(TestCase):
    """
    Test suite to reproduce and verify fix for Redis bytes decoding issue.
    Simulates Redis returning bytes (default redis-py behavior) instead of strings.
    """

    @patch('visits.services.matching.get_redis_connection')
    def test_find_candidates_handles_bytes_and_prefix(self, mock_get_conn):
        # Setup mock Redis
        mock_redis = MagicMock()
        mock_get_conn.return_value = mock_redis
        service = GeoMatchingService()

        # Simulate Redis returning bytes with prefix as (member, distance) tuples
        # This matches what redis.geosearch returns with withdist=True
        mock_redis.geosearch.return_value = [
            (b'nurse:999', 0.123),
            (b'nurse:1000', 0.456)
        ]

        # Execute
        results = service.find_candidates(30.0, 31.0)

        # Verify results are parsed correctly
        self.assertEqual(len(results), 2)

        # Check first result
        self.assertEqual(results[0]['nurse_id'], 999)
        self.assertIsInstance(results[0]['nurse_id'], int)
        self.assertEqual(results[0]['distance_km'], 0.123)

        # Check second result
        self.assertEqual(results[1]['nurse_id'], 1000)
        self.assertIsInstance(results[1]['nurse_id'], int)
