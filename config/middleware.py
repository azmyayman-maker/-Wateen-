from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
import logging
from typing import Tuple, Optional
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

User = get_user_model()


@database_sync_to_async
def get_user_and_agency_from_token(token: str) -> Tuple[object, Optional[str]]:
    """
    Extracts user and agency_id from JWT token.
    Returns (user, agency_id) tuple.
    """
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token["user_id"])
        agency_id = access_token.get("agency_id", None)
        return user, agency_id
    except (TokenError, User.DoesNotExist, KeyError) as e:
        logger.debug("WebSocket auth failed: %s", e)
        return AnonymousUser(), None


def extract_token_from_query_string(query_string: bytes) -> Optional[str]:
    """
    Extract JWT token from WebSocket query string (ws://...?token=xxx).

    SECURITY NOTE: Query string tokens are acceptable for WebSockets because
    browsers cannot attach custom headers during the WebSocket handshake.
    Token expiry is strictly enforced. Logging middleware should sanitize
    URLs containing 'token' parameter before writing to disk.
    """
    decoded = query_string.decode("utf-8")
    parsed = parse_qs(decoded)
    for key in ("token", "access_token", "jwt"):
        if key in parsed and parsed[key]:
            return parsed[key][0]
    return None


class JWTAuthMiddleware:
    """
    WebSocket Authentication Middleware using JWT.

    Extracts token from:
    1. Authorization header (Bearer <token>)
    2. Sec-WebSocket-Protocol header
    3. Query string (ws://...?token=xxx) - for browser WebSocket limitation

    Close Codes:
    - 4401: Authentication failure (missing/invalid/expired token)
    - 4003: Authorization failure (handled at consumer level)
    """

    WEBSOCKET_CLOSE_AUTH_FAILURE = 4401

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        token = None

        token = extract_token_from_query_string(scope.get("query_string", b""))

        if not token and b"authorization" in headers:
            auth_header = headers[b"authorization"].decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token and b"sec-websocket-protocol" in headers:
            protocols = [
                p.strip()
                for p in headers[b"sec-websocket-protocol"].decode().split(",")
            ]
            if len(protocols) >= 2 and protocols[0] in (
                "access_token",
                "Bearer",
                "jwt",
            ):
                token = protocols[1]
            elif len(protocols) == 1 and len(protocols[0]) > 20:
                token = protocols[0]

        if token:
            user, agency_id = await get_user_and_agency_from_token(token)
            if isinstance(user, AnonymousUser):
                logger.debug("WebSocket auth failed: invalid or expired token")
                scope["user"] = AnonymousUser()
                scope["agency_id"] = None
                return await self.app(scope, receive, send)
            scope["user"] = user
            scope["agency_id"] = agency_id
        else:
            logger.debug("WebSocket auth failed: no token provided")
            scope["user"] = AnonymousUser()
            scope["agency_id"] = None

        return await self.app(scope, receive, send)
