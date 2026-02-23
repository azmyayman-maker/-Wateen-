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
        logger.warning(f"WebSocket auth failed: {e}")
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    WebSocket Authentication Middleware using JWT.
    Extracts token from query string: ?token=ey...
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = urllib.parse.parse_qs(query_string)
        
        token = query_params.get('token', [None])[0]
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
            
        return await self.app(scope, receive, send)
