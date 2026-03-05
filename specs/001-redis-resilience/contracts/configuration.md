# Configuration Contracts

**Feature**: 001-redis-resilience
**Type**: Internal Configuration (No API endpoints)

This feature does not expose HTTP API endpoints. It provides configuration contracts for internal Django settings.

## Environment Variables

### REDIS_URL

**Format**: `redis://[:password@]host[:port][/database]`

**Examples**:
```
redis://localhost:6379/0
redis://:secret@redis-12345.cloud.redislabs.com:12345/0
rediss://:secret@secure-redis.example.com:6379/0  # TLS
```

**Behavior**:
- If not set: Falls back to in-memory cache (dev only)
- If set but unreachable: Falls back to in-memory cache (dev only) OR raises error (production)

### GDAL_LIBRARY_PATH (Optional)

**Format**: Absolute path to GDAL library file

**Examples**:
```
C:\OSGeo4W\bin\gdal304.dll
/usr/lib/libgdal.so
/opt/homebrew/lib/libgdal.dylib
```

**Behavior**:
- If not set on Windows: Auto-detection attempted
- If auto-detection fails: Warning displayed

## Configuration Output Contract

### Startup Log Messages

**Success (Redis Connected)**:
```
✅ Connected to Cloud Redis (12ms latency)
```

**Fallback (Dev Mode)**:
```
⚠️  Redis Unreachable. Using In-Memory Fallback (Dev Mode)
   Set REDIS_URL environment variable to enable Redis caching
```

**Error (Production)**:
```
❌ Redis Required: REDIS_URL not configured and DEBUG=False
   Configure REDIS_URL environment variable before deploying
```

### Doctor Script Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more checks failed |
| 2 | Configuration error (script misconfigured) |

## Django Settings Contract

### CACHES Configuration

```python
# Redis Mode
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "<REDIS_URL>",
    }
}

# Fallback Mode (DEBUG=True only)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "wateen-dev-cache",
    }
}
```

### CHANNEL_LAYERS Configuration

```python
# Redis Mode
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": ["<REDIS_URL>"]},
    }
}

# Fallback Mode (DEBUG=True only)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
```
