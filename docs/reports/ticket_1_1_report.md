# Technical Documentation Record: Phase 1, Ticket 1.1

## Executive Summary

This document records the successful scaffolding of the Docker infrastructure for the Wateen Modular Monolith application. The objective was to establish strict environment parity between development and production environments using Docker and Docker Compose. We have implemented a containerized setup for Django, PostgreSQL 16, and Redis 7, ensuring consistent runtime behavior across all deployment stages.

## Architecture Decisions

### Base Image: `python:3.11-slim`

- **Rationale**: We selected the `slim` variant over `alpine` or full `buster` images to balance image size and performance. `slim` provides a smaller footprint than full images while maintaining compatibility with standard Python wheels, avoiding the compilation overhead often encountered with Alpine for data science or heavy I/O libraries.

### Entrypoint Strategy (`entrypoint.sh`)

- **Rationale**: To prevent race conditions where the Django application attempts to connect to the database before it is fully initialized, we implemented a custom entrypoint script.
- **Mechanism**: The script uses `netcat` (`nc`) to poll the PostgreSQL host and port, blocking execution until the database is ready to accept connections. This ensures robust startup orchestration.

### Volume Mapping

- **Rationale**: We configured a bind mount (`.:/app`) for the `web` service in development.
- **Benefit**: This enables hot-reloading of code changes without requiring a container rebuild, significantly improving developer velocity while maintaining the containerized environment. A named volume (`postgres_data`) was used for the database to ensure data persistence across container restarts.

## File Manifest

| File                 | Description                                                                                                         |
| :------------------- | :------------------------------------------------------------------------------------------------------------------ |
| `Dockerfile`         | Defines the Python application environment, system dependencies (`netcat`, `gcc`), and non-root user configuration. |
| `docker-compose.yml` | Orchestrates the multi-container application (Django, Postgres, Redis), networking, and volume management.          |
| `entrypoint.sh`      | Bash script acting as the container entrypoint to handle database readiness checks before starting the app.         |
| `.env.example`       | Template file documenting executed environment variables required for the application.                              |
| `requirements.txt`   | Lists Python dependencies tailored for the Docker environment (e.g., `psycopg2-binary`).                            |
| `.dockerignore`      | Excludes unnecessary files (git history, pycache, venv) to optimize the build context.                              |

## Operational Guide

### 1. Setup Environment

Clone the repository and create your local environment file:

```bash
git clone <repository-url>
cd Wateen
cp .env.example .env
```

### 2. Build and Run

Build the images and start the services:

```bash
docker-compose up --build
```

The application will be accessible at `http://localhost:8000`.

### 3. Initialize Project (First Run Only)

If the project is empty, initialize the Django structure:

```bash
docker-compose run --rm web django-admin startproject config .
```

## Troubleshooting Log

### Issue: Docker Engine Not Running

- **Symptom**: `docker-compose` commands fail with connection errors to the Docker daemon.
- **Resolution**: Ensure the Docker Desktop (or Engine) service is active. On Linux, run `sudo systemctl start docker`. On Windows/Mac, launch the Docker Desktop application.

### Issue: DB_HOST Unbound Warning

- **Symptom**: Logs show a warning about `DB_HOST` being unbound during the initial build or script execution phases.
- **Context**: This warning often appears when running scripts that source the environment variables in a context where `.env` isn't automatically loaded or when intermediate containers run without the full simplified environment.
- **Impact**: Harmless in this setup as `docker-compose` explicitly injects these variables into the runtime containers.

## Verification Proof

- **Success Criteria**: Accessing `http://localhost:8000` in a web browser.
- **Observed Result**: The standard Django "The install worked successfully! Congratulations!" rocket page is displayed, confirming that the web container is running, receiving traffic, and the environment is correctly configured.
