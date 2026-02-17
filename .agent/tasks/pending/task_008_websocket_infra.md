# Task Identification

- **Task ID:** TASK-008
- **Task Name:** Ticket 2.2 — Real-time Infrastructure (WebSockets)
- **Status:** Pending
- **Assigned Execution Agent:** OpenCode
- **Assigned Review Authority:** Kilo Code

---

## 1) Context & Objective

The Wateen backend currently runs on WSGI via Gunicorn. To enable real-time dispatching features (Phase 2 of the Master Implementation Plan), we must transition to ASGI using Django Channels with Daphne as the ASGI server and Redis as the channel layer backend.

This task introduces the foundational WebSocket infrastructure. A basic `TestConsumer` implementing a "ping/pong" protocol will validate the entire stack: Daphne → Channels → Redis → Consumer → Response.

After completion, the system will:

- Serve HTTP and WebSocket traffic via a single ASGI entrypoint
- Have a functional WebSocket endpoint at `ws://localhost:8000/ws/test/`
- Use Redis as the channel layer backend (already running in Docker)

---

## 2) Technical Specifications

### Target Files

| File                        | Action | Responsibility                                  |
| --------------------------- | ------ | ----------------------------------------------- |
| `requirements/base.txt`     | MODIFY | Add `channels`, `daphne`, `channels-redis`      |
| `config/settings.py`        | MODIFY | ASGI config, `INSTALLED_APPS`, `CHANNEL_LAYERS` |
| `config/asgi.py`            | MODIFY | `ProtocolTypeRouter` with HTTP + WebSocket      |
| `visits/consumers.py`       | NEW    | `TestConsumer` (JsonWebsocketConsumer)          |
| `visits/routing.py`         | NEW    | WebSocket URL patterns                          |
| `docker/docker-compose.yml` | MODIFY | Switch `web` command from gunicorn to daphne    |

### Architecture Rules

- WebSocket consumer lives in the `visits` app (closest to dispatch domain)
- Consumer must NOT contain business logic — only protocol handling
- All imports must be lazy where Django requires it (ASGI bootstrap order)
- Channel layer configuration uses environment-compatible host references (`redis` hostname from Docker network)
- The `config/wsgi.py` file must NOT be deleted (backward compatibility)

### Technology Stack

| Component      | Version                            |
| -------------- | ---------------------------------- |
| Python         | 3.11                               |
| Django         | 5.0.2                              |
| channels       | 4.0.0                              |
| daphne         | 4.1.0                              |
| channels-redis | 4.2.0                              |
| Redis          | 7 (Alpine) — already in Docker     |
| Database       | PostGIS 16-3.4 — already in Docker |

---

## 3) Implementation Steps

### Step 1 — Add Dependencies to `requirements/base.txt`

Add the following under a new section header `# Real-time / WebSocket`:

```
channels==4.0.0
daphne==4.1.0
channels-redis==4.2.0
```

Place this section after the existing "Cache & Message Broker" section (after line 28).

---

### Step 2 — Update `config/settings.py`

**2a.** Add `'daphne'` as the **first** entry in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'daphne',                              # <-- MUST be first
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'users',
    'visits',
]
```

**2b.** Replace line 85 (`WSGI_APPLICATION = 'config.wsgi.application'`) with:

```python
ASGI_APPLICATION = 'config.asgi.application'
```

**2c.** Add `CHANNEL_LAYERS` configuration after the `ASGI_APPLICATION` line:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}
```

---

### Step 3 — Update `config/asgi.py`

Replace the entire contents of `config/asgi.py` with:

```python
"""
ASGI config for Wateen project.

It exposes the ASGI callable as a module-level variable named ``application``.
Handles both HTTP and WebSocket protocols via Django Channels.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early to populate AppRegistry
# This must happen before importing any models or consumers
django_asgi_app = get_asgi_application()

# Import after Django setup to avoid AppRegistryNotReady
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from visits.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

> **CRITICAL:** The `get_asgi_application()` call MUST execute before any Channels imports. This is a Django Channels requirement to avoid `AppRegistryNotReady` errors.

---

### Step 4 — Create `visits/consumers.py`

Create a new file `visits/consumers.py`:

```python
"""
WebSocket consumers for the visits app.

Contains the TestConsumer for validating WebSocket infrastructure.
"""

import logging

from channels.generic.websocket import JsonWebsocketConsumer

logger = logging.getLogger(__name__)


class TestConsumer(JsonWebsocketConsumer):
    """
    A simple WebSocket consumer for infrastructure validation.

    Accepts connections and responds to {"type": "ping"} with {"type": "pong"}.
    This consumer is used to verify the Channels/Redis/ASGI stack is working.
    """

    def connect(self):
        """Accept the WebSocket connection."""
        self.accept()
        logger.info("TestConsumer: WebSocket connection accepted")

    def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info("TestConsumer: WebSocket disconnected (code=%s)", close_code)

    def receive_json(self, content, **kwargs):
        """
        Handle incoming JSON messages.

        Responds to {"type": "ping"} with {"type": "pong"}.
        Unknown message types are logged and ignored.
        """
        message_type = content.get('type')

        if message_type == 'ping':
            self.send_json({'type': 'pong'})
        else:
            logger.warning(
                "TestConsumer: Unknown message type received: %s",
                message_type
            )
```

---

### Step 5 — Create `visits/routing.py`

Create a new file `visits/routing.py`:

```python
"""
WebSocket URL routing for the visits app.
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/test/$', consumers.TestConsumer.as_asgi()),
]
```

---

### Step 6 — Update `docker/docker-compose.yml`

Replace the `web` service `command` (line 24) from:

```yaml
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120
```

To:

```yaml
command: daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

> **NOTE:** Do NOT remove the `gunicorn` dependency from `requirements/base.txt`. It remains available for production WSGI fallback if needed.

---

## 4) Definition of Done (DoD)

### Functional Validation

- [ ] Container starts without errors (`docker compose up --build`)
- [ ] Daphne logs show `Listening on TCP address 0.0.0.0:8000`
- [ ] HTTP endpoints (`/admin/`, `/api/v1/`) continue to work under ASGI
- [ ] WebSocket connection to `ws://localhost:8000/ws/test/` succeeds
- [ ] Sending `{"type": "ping"}` returns `{"type": "pong"}`
- [ ] No database connection errors or locks

### Architectural Compliance

- [ ] `daphne` is the first entry in `INSTALLED_APPS`
- [ ] `ASGI_APPLICATION` points to `config.asgi.application`
- [ ] `CHANNEL_LAYERS` uses Redis host `redis` (Docker service name)
- [ ] Django ASGI app initialization happens before Channels imports in `asgi.py`
- [ ] Consumer contains zero business logic
- [ ] `config/wsgi.py` is preserved (not deleted)

### Standards Compliance

- [ ] All new files include module-level docstrings
- [ ] Logging uses `logging.getLogger(__name__)` pattern
- [ ] No hardcoded credentials or connection strings
- [ ] PEP 8 / project naming conventions followed

---

## 5) Acceptance Authority

The Reviewer (Kilo Code) must validate:

1. **Correctness** — WebSocket ping/pong works after Docker rebuild
2. **Architectural integrity** — ASGI bootstrap order is correct, no circular imports
3. **Stability** — HTTP endpoints unaffected, database accessible
4. **Maintainability** — Clean separation, proper logging, docstrings

Failure in any category rejects the task.

---

## Final Directive

The execution agent must not deviate from this specification.
The reviewer must reject the task if any section is partially satisfied.
