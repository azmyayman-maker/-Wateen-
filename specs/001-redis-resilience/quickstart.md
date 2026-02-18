# Quickstart: Infrastructure Resilience Upgrade

**Feature**: 001-redis-resilience
**Date**: 2026-02-18

## Quick Setup

### Option 1: Development (No Redis Required)

```bash
# No REDIS_URL needed - app uses in-memory fallback
python manage.py runserver

# Expected output:
# ⚠️  Redis Unreachable. Using In-Memory Fallback (Dev Mode)
```

### Option 2: With Cloud Redis

```bash
# Set Redis URL
export REDIS_URL="redis://:password@your-redis-host:port/0"

python manage.py runserver

# Expected output:
# ✅ Connected to Cloud Redis (15ms latency)
```

### Option 3: With Local Redis

```bash
# Start local Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

export REDIS_URL="redis://localhost:6379/0"

python manage.py runserver
```

## Diagnostics

Run the doctor script to check your environment:

```bash
python scripts/doctor.py
```

**Sample Output**:
```
Wateen Environment Diagnostics
==============================

✅ Python Version: 3.11.5
✅ Environment File: .env found
✅ Redis Connectivity: Connected (8ms)
✅ Database: Connected (12ms)
✅ GDAL: Available at /usr/lib/libgdal.so

Summary: 5 passed, 0 failed
```

## Windows GDAL Setup

If GDAL is missing on Windows:

1. **Install OSGeo4W**:
   ```
   Download from: https://trac.osgeo.org/osgeo4w/
   Select "Express Install" → GDAL
   ```

2. **Or set path manually**:
   ```powershell
   $env:GDAL_LIBRARY_PATH = "C:\OSGeo4W\bin\gdal304.dll"
   ```

3. **Verify**:
   ```bash
   python scripts/doctor.py
   ```

## Production Checklist

Before deploying to production:

- [ ] `DEBUG=False` in environment
- [ ] `REDIS_URL` is configured and accessible
- [ ] Run `python scripts/doctor.py` - all checks pass
- [ ] Verify startup shows "Connected to Cloud Redis" (not fallback)

## Troubleshooting

### "Redis Required" Error on Startup

**Cause**: `DEBUG=False` but no `REDIS_URL` configured

**Fix**: Set `REDIS_URL` environment variable

### Connection Refused

**Cause**: Redis URL points to unreachable server

**Fix**: 
1. Verify Redis server is running
2. Check firewall rules
3. Verify URL format and credentials

### GDAL Not Found (Windows)

**Cause**: GDAL not installed or path not detected

**Fix**: Install OSGeo4W or set `GDAL_LIBRARY_PATH`

### In-Memory Fallback in Production

**Cause**: `DEBUG=True` in production environment

**Fix**: Set `DEBUG=False` in production environment
