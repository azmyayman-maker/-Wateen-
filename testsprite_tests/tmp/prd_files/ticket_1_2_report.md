# Engineering Ticket Documentation

## Section A: Ticket Metadata

| Field | Value |
|-------|-------|
| **Ticket ID** | 1.2 |
| **Title** | Database & PostGIS Integration |
| **Status** | Implemented |
| **Date** | 2026-02-15 |

---

## Section B: Technical Summary

The database service has been upgraded from standard PostgreSQL to **PostGIS 16**, enabling native geospatial data storage and querying capabilities. This upgrade transforms the PostgreSQL instance into a fully-featured spatial database, supporting Wateen's location-based services including nurse dispatching and real-time tracking.

Key infrastructure changes include:

- **PostGIS Extension**: The `db` service now runs `postgis/postgis:16-3.4`, bundling PostgreSQL 16 with PostGIS 3.4.x.
- **GeoDjango Dependencies**: The application container (Dockerfile) now includes GDAL, GEOS, and PROJ libraries, enabling Django's GIS framework to interface with PostGIS.
- **Database Engine Migration**: Django's database backend has been switched from `django.db.backends.postgresql` to `django.contrib.gis.db.backends.postgis`.

This implementation follows the project's verified technical blueprint and maintains backward compatibility with existing PostgreSQL volumes while enabling new spatial data types (geometry, geography) and functions.

---

## Section C: File Manifest

### 1. `Dockerfile`

**Location:** `./Dockerfile`

**Changes:**
Added system dependencies for GeoDjango support via `apt-get install`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    netcat-openbsd \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*
```

| Package | Purpose |
|---------|---------|
| `gdal-bin` | GDAL command-line tools for geospatial data translation |
| `libgdal-dev` | GDAL development headers for Python bindings |
| `libgeos-dev` | GEOS geometry engine for spatial operations |
| `libproj-dev` | PROJ coordinate projection library |
| `gcc` | C compiler for building Python extensions |
| `libpq-dev` | PostgreSQL client development headers |

**Constraint Applied:** `--no-install-recommends` to minimize image size.

---

### 2. `docker-compose.yml`

**Location:** `./docker-compose.yml`

**Changes:**
Updated the `db` service image definition (line 84):

```yaml
db:
  image: postgis/postgis:16-3.4
```

**Previous Value:** `postgres:16-alpine`

**Preserved Elements:**
- `postgres_data` volume mounted to `/var/lib/postgresql/data/`
- Healthcheck using `pg_isready`
- Network isolation via `wateen_network`
- Resource limits and logging configuration

---

### 3. `config/settings.py`

**Location:** `./config/settings.py`

**Changes:**

1. **Import Statement** (line 14):
   ```python
   import os
   ```

2. **INSTALLED_APPS** (line 41):
   ```python
   INSTALLED_APPS = [
       ...
       'django.contrib.gis',
   ]
   ```

3. **DATABASES Configuration** (lines 77-86):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.contrib.gis.db.backends.postgis',
           'NAME': os.environ.get('DB_NAME', 'wateen'),
           'USER': os.environ.get('DB_USER', 'wateen'),
           'PASSWORD': os.environ.get('DB_PASSWORD', 'wateen_secret'),
           'HOST': os.environ.get('DB_HOST', 'db'),
           'PORT': os.environ.get('DB_PORT', '5432'),
       }
   }
   ```

**Previous Engine:** `django.db.backends.postgresql`

---

## Section D: Configuration Changes

### Environment Variables

No new `.env` variables are required for this implementation. The existing database credentials are reused:

| Variable | Usage | Default |
|----------|-------|---------|
| `DB_NAME` | Database name | `wateen` |
| `DB_USER` | Database user | `wateen` |
| `DB_PASSWORD` | Database password | `wateen_secret` |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |

### System Dependencies

The following packages are now **hard requirements** for the container build:

- `gdal-bin` — Required for GeoDjango's `GDAL_LIBRARY_PATH` detection
- `libgdal-dev` — Required for compiling GDAL Python bindings
- `libgeos-dev` — Required for spatial geometry operations
- `libproj-dev` — Required for coordinate reference system transformations

**Note:** These dependencies are installed at container build time and do not affect the host system.

---

## Section E: Verification Steps

### 1. Rebuild and Deploy

**⚠️ Warning:** The following command destroys the existing PostgreSQL volume. This is necessary to allow the PostGIS image to initialize the extension system.

```bash
docker-compose down -v
docker-compose up -d --build
```

For non-destructive verification (existing data retained):
```bash
docker-compose up -d --build
docker-compose exec db psql -U wateen -d wateen -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 2. Verify PostGIS Extension

```bash
docker-compose exec db psql -U wateen -d wateen -c "SELECT PostGIS_Version();"
```

**Expected Output:**
```
                            postgis_version                            
-----------------------------------------------------------------------
 3.4 USE_GEOS=1, USE_PROJ=1, USE_STATS=1
(1 row)
```

### 3. Verify Django Application

Check the `web` container logs for successful startup:

```bash
docker-compose logs -f web
```

**Success Indicators:**
- No `ImproperlyConfigured` exceptions regarding GDAL or GEOS libraries
- Application binds to port 8000 without errors
- Database migrations (if any) execute successfully

**Failure Indicators:**
- `Could not find the GDAL library` — Indicates missing `gdal-bin` or incorrect path
- `Could not find the GEOS library` — Indicates missing `libgeos-dev`

### 4. Verify GeoDjango in Django Shell

```bash
docker-compose exec web python manage.py shell
```

```python
>>> from django.contrib.gis.geos import Point
>>> p = Point(30.0, 31.0)
>>> p.wkt
'POINT (30 31)'
```

---

## Section F: Architectural Compliance

### Modular Monolith Alignment

This implementation enables the **Modular Monolith** architecture to handle location data within the single `db` instance. The PostGIS extension coexists with standard PostgreSQL tables, allowing:

- **Spatial Queries**: Location-aware queries for nurse proximity, service area coverage, and dispatch optimization
- **Data Locality**: All location data remains in the primary database, avoiding cross-service data synchronization issues during the monolithic phase
- **Future Decomposition**: When the architecture evolves toward microservices, PostGIS can be migrated to a dedicated spatial service or retained as a shared data layer

### Redis Geo Strategy Integration

PostGIS provides the **persistent storage backing** for the Redis Geo strategy:

| Layer | Technology | Role |
|-------|------------|------|
| **Hot Store** | Redis Geo | Real-time location tracking, geospatial indexing for active sessions |
| **Warm Store** | PostGIS | Persistent storage for location logs, historical tracking, and analytics |

This dual-layer approach enables:
1. Fast geospatial queries for live dispatch operations (Redis)
2. Durable storage for compliance, auditing, and route optimization ML training (PostGIS)

### Security Considerations

- Database credentials continue to be sourced from environment variables, not hardcoded
- The `db` service remains isolated on the internal `wateen_network` without external port exposure
- PostGIS does not introduce additional attack surface beyond standard PostgreSQL

---

## Section G: Rollback Procedure

If issues arise, revert to standard PostgreSQL:

1. Restore `docker-compose.yml`:
   ```yaml
   image: postgres:16-alpine
   ```

2. Restore `config/settings.py`:
   ```python
   'ENGINE': 'django.db.backends.postgresql',
   ```

3. Remove `'django.contrib.gis'` from `INSTALLED_APPS`

4. Remove GeoDjango dependencies from `Dockerfile`

5. Rebuild:
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   ```

---

*Documentation generated for Wateen Healthcare Platform — Engineering Team Reference.*