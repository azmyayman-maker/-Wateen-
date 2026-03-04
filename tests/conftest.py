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
