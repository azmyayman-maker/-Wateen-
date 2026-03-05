# Quickstart: Redis Cloud Integration

**Feature**: 003-redis-cloud-integration  
**Date**: 2026-02-18

## Prerequisites

- Redis Cloud account with a database created
- Redis Cloud connection URL (provided by Redis Cloud dashboard)
- Docker and Docker Compose installed
- Python 3.11+ environment

## Setup Steps

### 1. Configure Environment Variables

Add the Redis Cloud URL to your `.env` file:

```bash
# .env
REDIS_URL=redis://:your-password@your-redis-host:port/0
```

**Important**: Never commit the actual `.env` file with credentials. Use `.env.example` as a template.

### 2. Update Docker Configuration

The local Redis container has been removed from `docker-compose.yml`. Ensure your environment has:

- Network access to Redis Cloud endpoints
- Proper firewall rules to allow outbound connections to Redis Cloud

### 3. Verify Configuration

Run the management command to test Redis Cloud connectivity:

```bash
# Inside Docker container
docker compose -f docker/docker-compose.yml exec web python manage.py test_redis

# Or locally with environment loaded
python manage.py test_redis
```

Expected output:

```
Testing Redis Cloud connectivity...
Cache: OK
Channel Layer: OK
Redis Connected Successfully
```

### 4. Start the Application

```bash
# Start all services
docker compose -f docker/docker-compose.yml up -d

# Check logs
docker compose -f docker/docker-compose.yml logs -f web
```

## Configuration Reference

### Django Settings

The following settings are configured in `config/settings.py`:

```python
# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
            },
        },
        "KEY_PREFIX": "wateen",
    },
}

# Channel layer configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL")],
        },
    },
}
```

### Environment Variables

| Variable    | Required | Description                                         |
| ----------- | -------- | --------------------------------------------------- |
| `REDIS_URL` | Yes      | Full Redis Cloud connection URL with authentication |

## Troubleshooting

### Connection Timeout

If you see connection timeout errors:

1. Verify network connectivity to Redis Cloud
2. Check firewall rules
3. Verify the Redis Cloud URL is correct
4. Ensure Redis Cloud database is active

### Graceful Degradation Mode

If Redis is unavailable, the application will:

- Log warnings about Redis unavailability
- Fall back to database queries for cached data
- Disable WebSocket features with user notification

Check logs for degradation messages:

```bash
docker compose -f docker/docker-compose.yml logs web | grep -i redis
```

### Connection Pool Exhaustion

If you see "Connection pool exhausted" errors:

1. Check the number of application instances
2. Monitor connection usage: `redis-cli info clients`
3. Consider increasing `max_connections` if Redis Cloud plan allows

## Testing

### Run Integration Tests

```bash
# Run Redis Cloud integration tests
pytest tests/test_redis_cloud.py -v

# Run all tests
pytest -v
```

### Manual Cache Test

```python
# Django shell
python manage.py shell

>>> from django.core.cache import cache
>>> cache.set('test_key', 'test_value', 60)
>>> cache.get('test_key')
'test_value'
```

### Manual Channel Layer Test

```python
# Django shell
python manage.py shell

>>> from channels.layers import get_channel_layer
>>> from asgiref.sync import async_to_sync
>>>
>>> channel_layer = get_channel_layer()
>>> async_to_sync(channel_layer.send)('test_channel', {'type': 'test.message', 'text': 'hello'})
>>> async_to_sync(channel_layer.receive)('test_channel')
{'type': 'test.message', 'text': 'hello'}
```

## Rollback

If issues arise, rollback to local Redis:

1. Restore the `redis` service in `docker-compose.yml`
2. Update `REDIS_URL` to point to local Redis: `redis://redis:6379/0`
3. Restart services: `docker compose -f docker/docker-compose.yml up -d`
