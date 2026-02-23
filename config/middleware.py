import urllib.parse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token: str):
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except Exception as e:
        logger.warning("WebSocket auth failed: %s", e)
        return AnonymousUser()

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
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
            
        return await self.app(scope, receive, send)
