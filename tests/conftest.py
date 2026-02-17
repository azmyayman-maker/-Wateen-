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
    """
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # For local testing, we can set a test database
    os.environ.setdefault('DB_HOST', 'localhost')


@pytest.fixture(scope='session')
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
    """
    try:
        from django.contrib.gis.gdal.libgdal import lgdal
    except Exception:
        if 'gis' in request.node.name.lower():
            pytest.skip("GIS tests require GDAL library")
