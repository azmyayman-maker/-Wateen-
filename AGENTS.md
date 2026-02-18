# Wateen Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-18

## Active Technologies
- Python 3.11+ + Django 5.2, Django REST Framework, django-redis, channels_redis, django.contrib.gis (PostGIS) (001-redis-resilience)
- PostgreSQL with PostGIS extension (001-redis-resilience)
- Python 3.11+ + Django 5.2, Django REST Framework, redis-py, psycopg2, pytest, flake8 (001-audit-cleanup)

- Python 3.11+ + Django 5.2, Django REST Framework, PostGIS (django.contrib.gis) (001-pricing-engine)

## Project Structure

```text
config/
users/
visits/
tests/
```

## Commands

pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 001-audit-cleanup: Added Python 3.11+ + Django 5.2, Django REST Framework, redis-py, psycopg2, pytest, flake8
- 001-redis-resilience: Added Python 3.11+ + Django 5.2, Django REST Framework, django-redis, channels_redis, django.contrib.gis (PostGIS)

- 001-pricing-engine: Added Python 3.11+ + Django 5.2, Django REST Framework, PostGIS (django.contrib.gis)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
