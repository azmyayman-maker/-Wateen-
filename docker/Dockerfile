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
# curl                    → HTTP health checking in docker-compose.yml
# binutils                → Binary utilities (required for GDAL linking)
# gdal-bin, libgdal-dev   → GDAL library for GeoDjango
# python3-gdal            → Python GDAL bindings
# libgeos-dev             → GEOS geometry engine for spatial operations
# libproj-dev             → PROJ coordinate projection library
# tesseract-ocr           → OCR engine for KYC document processing
# tesseract-ocr-ara       → Arabic language data for Tesseract
# libgl1                  → OpenCV headless rendering dependency (replaces libgl1-mesa-glx)
# --------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    netcat-openbsd \
    curl \
    binutils \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libgeos-dev \
    libproj-dev \
    tesseract-ocr \
    tesseract-ocr-ara \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (base + dev for testing)
COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt
RUN pip install --upgrade pip && pip install -r requirements/dev.txt

# Copy project
COPY . .

# Set entrypoint (ensure execute permissions)
RUN chmod +x /app/docker/entrypoint.sh
ENTRYPOINT ["/app/docker/entrypoint.sh"]
