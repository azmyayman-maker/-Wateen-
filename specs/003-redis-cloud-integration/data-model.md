# Data Model: Redis Cloud Integration

**Feature**: 003-redis-cloud-integration  
**Date**: 2026-02-18

## Overview

This feature does not introduce new database entities. It is a configuration change that affects how existing data is cached and how real-time communication is handled.

## Existing Entities Affected

### Cache Data Structure

Redis Cloud will store cached data with the following key patterns:

| Key Pattern                       | Description                | TTL        |
| --------------------------------- | -------------------------- | ---------- |
| `wateen:user:{user_id}`           | Cached user profile data   | 1 hour     |
| `wateen:visit:{visit_id}`         | Cached visit details       | 15 minutes |
| `wateen:nurse:available:{region}` | Available nurses by region | 5 minutes  |
| `wateen:pricing:estimate:{hash}`  | Cached pricing estimates   | 30 minutes |

### Channel Layer Groups

Redis Cloud will handle WebSocket message routing:

| Group Name             | Purpose                        | Consumers               |
| ---------------------- | ------------------------------ | ----------------------- |
| `visit_{visit_id}`     | Visit status updates           | Patient, assigned nurse |
| `nurse_{nurse_id}`     | Nurse-specific notifications   | Nurse dashboard         |
| `patient_{patient_id}` | Patient-specific notifications | Patient app             |

## Configuration Entities

### Redis Connection Configuration

No database entity required. Configuration is stored in:

- **Environment Variable**: `REDIS_URL`
- **Format**: `redis://:password@host:port/database`
- **Django Settings**: `CACHES` and `CHANNEL_LAYERS` dictionaries

### Connection Pool Settings

| Setting                  | Value | Description                      |
| ------------------------ | ----- | -------------------------------- |
| `max_connections`        | 50    | Maximum connections per instance |
| `retry_on_timeout`       | True  | Retry on connection timeout      |
| `socket_timeout`         | 5     | Socket timeout in seconds        |
| `socket_connect_timeout` | 5     | Connection timeout in seconds    |

## No Schema Changes Required

This feature does not require any database migrations or schema changes.

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Django App    │────▶│   Redis Cloud   │────▶│   WebSocket     │
│   (Cache API)   │     │   (Cache Store) │     │   Clients       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │     │   Channel       │
│   (Fallback)    │     │   Layer         │
└─────────────────┘     └─────────────────┘
```

### Cache Read Flow

1. Application requests cached data
2. If Redis available: return cached data or miss
3. If Redis unavailable: fall back to database query
4. Log degradation event if fallback used

### WebSocket Message Flow

1. Consumer sends message to channel group
2. Redis Cloud routes message to all group consumers
3. If Redis unavailable: disable WebSocket features, notify users
