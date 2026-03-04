# Ticket Documentation: Ticket 2.2 - Real-time Infrastructure (WebSockets)

## 1. Metadata

- **Status:** Verified
- **Date:** 2026-02-17
- **Phase:** Phase 2 (Core Visit Management)
- **Author:** Wateen AI (Architecture) / OpenCode (Implementation)

## 2. Technical Summary

The Django project has been successfully transitioned from a synchronous WSGI architecture to an asynchronous **ASGI** architecture to support real-time capabilities. **Daphne** has been introduced as the ASGI interface server, serving both HTTP and WebSocket traffic. **Redis** (via `channels_redis`) is configured as the Channel Layer backing store, enabling scalable message passing between instances. A "Ping/Pong" mechanism was implemented and verified to ensure the full WebSocket stack (Daphne → Channels → Redis → Consumer) is operational.

## 3. File Manifest

- `config/asgi.py`: Entry point for ASGI lifecycle. Configured `ProtocolTypeRouter` to handle `http` via Django's ASGI app and `websocket` via Channels' `AuthMiddlewareStack`.
- `config/settings.py`: Added `'daphne'` (must be first) and `'channels'` to `INSTALLED_APPS`. Configured `CHANNEL_LAYERS` to use Redis. Replaced `WSGI_APPLICATION` with `ASGI_APPLICATION`.
- `visits/routing.py`: Defined `websocket_urlpatterns` routing `/ws/test/` to the `TestConsumer`.
- `visits/consumers.py`: Implemented `TestConsumer`, a `JsonWebsocketConsumer` that responds to `{"type": "ping"}` with `{"type": "pong"}` for connectivity verification.
- `tests/test_websockets_infrastructure.py`: Comprehensive Pytest suite utilizing `WebsocketCommunicator` to verify connection success, ping/pong message exchange, and graceful disconnection.

## 4. Configuration Changes

- **ASGI_APPLICATION**: Set to `'config.asgi.application'`
- **CHANNEL_LAYERS**: Configured to use `channels_redis.core.RedisChannelLayer`
- **Redis Host**: `redis` (Docker service name from `wateen_network`)
- **Redis Port**: `6379`

## 5. Verification & Testing

### Automated Testing:

```bash
docker compose exec web pytest tests/test_websockets_infrastructure.py -v
```

_(Note: confirmed passing 10/10 tests including connection, ping/pong, and routing checks)_

### Manual Verification:

1. Ensure Docker is running: `docker compose up -d`
2. Use a WebSocket client (e.g., `wscat` or browser console):
   ```javascript
   // In Browser Console
   const ws = new WebSocket("ws://localhost:8000/ws/test/");
   ws.onopen = () => ws.send(JSON.stringify({ type: "ping" }));
   ws.onmessage = (e) => console.log("Received:", JSON.parse(e.data));
   // Expected Output: Received: {type: "pong"}
   ```

## 6. Architectural Compliance

- **Modular Monolith:** WebSocket routing is defined within the `visits` app but hooked into the project-level `asgi.py`, decoupling real-time logic from synchronous HTTP views.
- **Scalability:** The use of `RedisChannelLayer` allows for horizontal scaling. Multiple Daphne workers can communicate and broadcast messages via the shared Redis instance.
