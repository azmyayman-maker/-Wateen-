# Wateen Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-18

## Active Technologies
- Python 3.11+ + Django 5.2, Django REST Framework, django-redis, channels_redis, django.contrib.gis (PostGIS) (001-redis-resilience)
- PostgreSQL with PostGIS extension (001-redis-resilience)

- Python 3.11+ + Django 5.2, Django REST Framework, PostGIS (django.contrib.gis) (001-pricing-engine)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 001-redis-resilience: Added Python 3.11+ + Django 5.2, Django REST Framework, django-redis, channels_redis, django.contrib.gis (PostGIS)

- 001-pricing-engine: Added Python 3.11+ + Django 5.2, Django REST Framework, PostGIS (django.contrib.gis)
- 002-pricing-engine-remediation: Fixed dynamic distance calculation, nurse availability filtering, timezone awareness, async logging

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
