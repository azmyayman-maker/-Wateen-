# Research: Redis Cloud Integration

**Feature**: 003-redis-cloud-integration  
**Date**: 2026-02-18

## Research Tasks

### 1. Redis Cloud Connection URL Format

**Decision**: Use standard Redis URL format with authentication

**Rationale**: Redis Cloud provides a standard Redis URL format that includes authentication credentials:

```
redis://:password@host:port/database
```

**Alternatives Considered**:

- Separate environment variables for host, port, password - Rejected because Redis Cloud provides a single URL, and splitting it adds complexity
- TLS connection string (`rediss://`) - Not needed as the provided URL uses standard Redis protocol

### 2. Django Redis Cache Backend Configuration

**Decision**: Use django-redis with connection pooling

**Rationale**: django-redis is already in the project dependencies and provides:

- Native Django cache backend integration
- Connection pooling support
- Serialization options
- Graceful degradation capabilities

**Configuration Pattern**:

```python
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
```

**Alternatives Considered**:

- Built-in Django database cache - Rejected because Redis Cloud is already provisioned
- Memcached - Rejected because Redis provides additional features (persistence, data structures)

### 3. Django Channels Redis Channel Layer

**Decision**: Use channels-redis with Redis Cloud URL

**Rationale**: channels-redis is already configured in the project and supports:

- Cross-instance communication
- Message groups for targeted broadcasts
- Connection to external Redis servers

**Configuration Pattern**:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL")],
        },
    },
}
```

**Alternatives Considered**:

- In-memory channel layer - Rejected because it doesn't support multiple instances
- RabbitMQ - Rejected because Redis Cloud is already provisioned and simpler

### 4. Graceful Degradation Strategy

**Decision**: Implement cache fallback with database queries and WebSocket feature disable

**Rationale**: For a healthcare application, availability is critical. When Redis is unavailable:

- Cache operations should fall back to database queries (slower but functional)
- WebSocket features should be disabled with user notification (not critical for core functionality)
- Application should log warnings and periodically attempt reconnection

**Implementation Approach**:

- Use try/except around cache operations with fallback to database
- Implement health check for channel layer availability
- Add middleware or context processor to indicate degraded mode

**Alternatives Considered**:

- Fail fast - Rejected because healthcare application needs to remain operational
- Silent fallback - Rejected because users need to know real-time features are unavailable

### 5. Docker Compose Configuration Changes

**Decision**: Remove local Redis service, pass REDIS_URL as environment variable

**Rationale**: Using Redis Cloud eliminates the need for a local Redis container:

- Reduces resource usage
- Eliminates conflict between local and cloud Redis
- Simplifies deployment

**Changes Required**:

1. Remove `redis` service from docker-compose.yml
2. Remove `redis_data` volume
3. Remove `redis` dependency from `web` service
4. Add `REDIS_URL` to web service environment

**Alternatives Considered**:

- Keep local Redis as fallback - Rejected because it adds complexity and Redis Cloud is the production target
- Use Docker environment variable substitution - Rejected in favor of explicit env_file configuration

### 6. Connection Pool Sizing

**Decision**: 50 connections per application instance

**Rationale**:

- Redis Cloud typical plans support 50-150 concurrent connections
- 50 connections per instance allows for 2-3 application instances
- Connection pooling reduces connection overhead
- Matches the clarification answer from user

**Alternatives Considered**:

- 10 connections - Rejected because insufficient for production load
- 100 connections - Rejected because may exceed Redis Cloud plan limits
- No limit - Rejected because can lead to connection exhaustion

### 7. Management Command for Connection Testing

**Decision**: Create `test_redis` management command

**Rationale**: A dedicated management command provides:

- Easy verification of Redis Cloud connectivity
- Clear output for operations team
- Can be run in CI/CD pipelines
- Tests both cache and channel layer functionality

**Command Structure**:

```python
# visits/management/commands/test_redis.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from channels.layers import get_channel_layer

class Command(BaseCommand):
    help = 'Test Redis Cloud connectivity'

    def handle(self, *args, **options):
        # Test cache
        # Test channel layer
        # Output results
```

**Alternatives Considered**:

- Shell script using redis-cli - Rejected because it doesn't test Django integration
- Health check endpoint - Rejected because management command is more versatile

## Dependencies Verified

| Dependency     | Version | Status            | Notes                 |
| -------------- | ------- | ----------------- | --------------------- |
| redis          | 5.0.1   | Already installed | Python Redis client   |
| django-redis   | 6.0.0   | Already installed | Django cache backend  |
| channels-redis | 4.2.0   | Already installed | Channel layer backend |

## No NEEDS CLARIFICATION Items

All technical decisions have been resolved through research and the clarification workflow.
