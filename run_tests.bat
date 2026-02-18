@echo off
REM =============================================================================
REM Wateen Project - Docker Test Runner (Windows)
REM =============================================================================
REM This script runs tests inside the Docker container to bypass local GDAL
REM issues on Windows. The container has all geospatial libraries installed.
REM =============================================================================

echo Running tests inside Docker container...
echo.

REM Change to docker directory and run tests, then restore directory
pushd docker
docker-compose run --rm web python manage.py test visits --verbosity=2
set TEST_EXIT_CODE=%ERRORLEVEL%
popd

echo.
echo Tests completed.
exit /b %TEST_EXIT_CODE%
