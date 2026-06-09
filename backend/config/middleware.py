import logging
from typing import Optional, Tuple

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)

User = get_user_model()


def _mask_token(token: str) -> str:
    """Return a masked version of the token for safe logging."""
    if token and len(token) > 8:
        return f"{token[:8]}..."
    return "[token_redacted]"


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
        logger.debug(
            "WebSocket auth failed for token=%s: %s",
            _mask_token(token) if token else "none",
            e,
        )
        return AnonymousUser(), None


# Removed extract_token_from_query_string due to medical privacy risks.
# Tokens should exclusively be passed via headers (Authorization or Sec-WebSocket-Protocol)


class JWTAuthMiddleware:
    """
    WebSocket Authentication Middleware using JWT.

    Extracts token from:
    1. Authorization header (Bearer <token>)
    2. Sec-WebSocket-Protocol header

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
            elif len(protocols) == 1 and len(protocols[0].split(".")) == 3:
                token = protocols[0]

        if token:
            user, agency_id = await get_user_and_agency_from_token(token)
            if isinstance(user, AnonymousUser):
                logger.debug(
                    "WebSocket auth failed: invalid or expired token=%s",
                    _mask_token(token),
                )
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
