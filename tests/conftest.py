"""
Pytest configuration and fixtures for Wateen project tests.

This module provides test configuration that allows running tests
outside of Docker by mocking GIS dependencies when needed.
"""

import pytest
import os


def pytest_configure(config):
    """
    Configure pytest with Django settings.

    For local testing without GDAL, we can skip GIS-related tests.
    Test classes or methods that use GIS should be marked with @pytest.mark.gis.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DB_HOST", "localhost")


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Configure Django database for tests.

    This fixture ensures database is available for tests that need it.
    """
    pass


@pytest.fixture(autouse=True)
def allow_gis_exceptions(request):
    """
    Skip tests that require GIS if GDAL is not available.

    Tests marked with @pytest.mark.gis will be skipped when GDAL is missing.
    """
    try:
        from django.contrib.gis.gdal.libgdal import lgdal
    except (ImportError, OSError):
        marker = request.node.get_closest_marker("gis")
        if marker is not None:
            pytest.skip("GIS tests require GDAL library")


# ============================================================================
# P4-T5: Dispatch & Pricing QA Fixtures
# ============================================================================


@pytest.fixture
def api_client():
    """DRF API client for testing API endpoints."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def overlapping_agencies():
    """Fixture providing 3 agencies with overlapping coverage polygons."""
    from tests.fixtures.dispatch_pricing_fixtures import create_overlapping_agencies

    return create_overlapping_agencies()


@pytest.fixture
def concurrent_offers(num_nurses=10):
    """Fixture providing visit with multiple pending offers for concurrency tests."""
    from tests.fixtures.dispatch_pricing_fixtures import create_concurrent_offers

    return create_concurrent_offers(num_nurses=num_nurses)


@pytest.fixture
def pricing_test_matrix():
    """Fixture providing known input/output pairs for pricing formula tests."""
    from tests.fixtures.dispatch_pricing_fixtures import PRICING_TEST_MATRIX

    return PRICING_TEST_MATRIX


@pytest.fixture
def quality_score_weights():
    """Fixture providing QualityScore formula weights."""
    from tests.fixtures.dispatch_pricing_fixtures import QUALITY_SCORE_WEIGHTS

    return QUALITY_SCORE_WEIGHTS
