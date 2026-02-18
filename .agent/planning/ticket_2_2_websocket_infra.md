# Ticket 2.2 — Real-time Infrastructure (WebSockets)

## Objective

Transition Django backend from WSGI to ASGI using Django Channels + Daphne + Redis.
Implement a basic `TestConsumer` (ping/pong) to validate the WebSocket stack end-to-end.

---

## Prerequisites (Already Verified)

- Redis service defined in `docker/docker-compose.yml` (host: `redis`, port: `6379`, `wateen_network`)
- Django project module is `config/` (not `wateen_project/`)
- Existing `config/asgi.py` with default Django ASGI setup
- `config/settings.py` uses `WSGI_APPLICATION = 'config.wsgi.application'`
- Requirements managed via `requirements/base.txt`
- `visits` app exists and is registered in `INSTALLED_APPS`
- Python 3.11-slim base image in `docker/Dockerfile`
- Django 5.0.2

---

## Proposed Changes

### Dependencies

#### [MODIFY] `requirements/base.txt`

Add: `channels==4.0.0`, `daphne==4.1.0`, `channels-redis==4.2.0`

### Configuration

#### [MODIFY] `config/settings.py`

1. Add `'daphne'` as first entry in `INSTALLED_APPS`
2. Replace `WSGI_APPLICATION` with `ASGI_APPLICATION = 'config.asgi.application'`
3. Add `CHANNEL_LAYERS` pointing to `redis://redis:6379/0`

#### [MODIFY] `config/asgi.py`

Upgrade to `ProtocolTypeRouter` with HTTP + WebSocket support via `AuthMiddlewareStack`.

### WebSocket Consumer & Routing

#### [NEW] `visits/consumers.py`

`TestConsumer` (JsonWebsocketConsumer): accepts connections, responds to `ping` with `pong`.

#### [NEW] `visits/routing.py`

WebSocket URL pattern: `ws/test/` → `TestConsumer`

### Docker

#### [MODIFY] `docker/docker-compose.yml`

Replace gunicorn WSGI command with daphne ASGI command.

---

## Verification Plan

1. Docker rebuild + test container logs for Daphne startup
2. WebSocket ping/pong test via `channels.testing.WebsocketCommunicator`
3. Database verification via Postgres MCP (schemas, tables, health)
