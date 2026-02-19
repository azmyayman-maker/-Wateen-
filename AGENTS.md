# Wateen Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-18

## Active Technologies
- Python 3.11+ + Django 5.2, Django REST Framework, django-redis, channels_redis, django.contrib.gis (PostGIS) (001-redis-resilience)
- PostgreSQL with PostGIS extension (001-redis-resilience)
- Python 3.11+ + Django 5.2, Django REST Framework, redis-py, psycopg2, pytest, flake8 (001-audit-cleanup)
- TypeScript 5.x / Next.js 14 (App Router) + Next.js 14, React 18, Tailwind CSS, next/font (Cairo), ESLint (004-frontend-init)
- N/A (frontend only, no data persistence) (004-frontend-init)
- Python 3.11+ + Django 5.2, redis-py, psycopg2, pytest, pytest-django, pytest-asyncio (005-infra-verification)
- PostgreSQL with PostGIS extension, Redis 7 (005-infra-verification)

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
- 005-infra-verification: Added Python 3.11+ + Django 5.2, redis-py, psycopg2, pytest, pytest-django, pytest-asyncio
- 004-frontend-init: Added TypeScript 5.x / Next.js 14 (App Router) + Next.js 14, React 18, Tailwind CSS, next/font (Cairo), ESLint
- 001-audit-cleanup: Added Python 3.11+ + Django 5.2, Django REST Framework, redis-py, psycopg2, pytest, flake8


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
