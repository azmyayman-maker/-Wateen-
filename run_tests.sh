#!/bin/bash
# =============================================================================
# Wateen Project - Docker Test Runner (Linux/Mac)
# =============================================================================
# This script runs tests inside the Docker container to bypass local GDAL
# issues. The container has all geospatial libraries installed.
# =============================================================================

echo "Running tests inside Docker container..."
echo

# Change to docker directory and run tests
cd docker
docker-compose run --rm web python manage.py test visits --verbosity=2

echo
echo "Tests completed."
