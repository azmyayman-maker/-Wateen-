#!/bin/bash
# =============================================================================
# Wateen Project - Docker Test Runner (Linux/Mac)
# =============================================================================
# This script runs tests inside the Docker container to bypass local GDAL
# issues. The container has all geospatial libraries installed.
# =============================================================================

set -e  # Exit on any error

echo "Running tests inside Docker container..."
echo

# Change to docker directory and run tests (exit if cd fails)
cd docker || exit 1

# Run tests and propagate exit code
docker-compose run --rm web python manage.py test visits --verbosity=2
