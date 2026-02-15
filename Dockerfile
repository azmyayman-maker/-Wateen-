FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
# --------------------------------------------------------------------------
# gcc, libpq-dev          → PostgreSQL adapter compilation
# netcat-openbsd          → TCP health checking in entrypoint.sh
# gdal-bin, libgdal-dev   → GDAL library for GeoDjango
# libgeos-dev             → GEOS geometry engine for spatial operations
# libproj-dev             → PROJ coordinate projection library
# --------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    netcat-openbsd \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
