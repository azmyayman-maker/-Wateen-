from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
import logging
from typing import Tuple, Optional

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
        user = User.objects.get(id=access_token['user_id'])
        # Extract agency_id from token claims (set by CustomTokenObtainPairSerializer)
        agency_id = access_token.get('agency_id', None)
        return user, agency_id
    except (TokenError, User.DoesNotExist) as e:
        logger.warning("WebSocket auth failed: %s", e)
        return AnonymousUser(), None

class JWTAuthMiddleware:
    """
    WebSocket Authentication Middleware using JWT.
    Extracts token from Authorization header or Sec-WebSocket-Protocol.
    
    SECURITY: Tokens in URL query strings are explicitly REJECTED to prevent
    exposure in server logs, browser history, and proxy logs (medical privacy risk).
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers', []))
        token = None

        # SECURITY: Reject tokens passed in query string - medical privacy risk
        query_string = scope.get('query_string', b'').decode()
        if 'token=' in query_string or 'jwt=' in query_string or 'access_token=' in query_string:
            logger.warning("SECURITY: Rejected WebSocket connection with token in query string")
            scope['user'] = AnonymousUser()
            return await self.app(scope, receive, send)

        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token and b'sec-websocket-protocol' in headers:
            protocols = [p.strip() for p in headers[b'sec-websocket-protocol'].decode().split(',')]
            if len(protocols) >= 2 and protocols[0] in ('access_token', 'Bearer', 'jwt'):
                token = protocols[1]
            elif len(protocols) == 1 and len(protocols[0]) > 20: 
                token = protocols[0]

        if token:
            user, agency_id = await get_user_and_agency_from_token(token)
            scope['user'] = user
            scope['agency_id'] = agency_id  # For AgencyConsumer B2B2C support
        else:
            scope['user'] = AnonymousUser()
            scope['agency_id'] = None
            
        return await self.app(scope, receive, send)
