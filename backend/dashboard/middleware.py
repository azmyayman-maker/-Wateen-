import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from users.models import CustomUser


@database_sync_to_async
def get_user(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = CustomUser.objects.get(id=payload['user_id'])
        if user.role not in ['AGENCY_ADMIN', 'SUPERADMIN'] or not user.is_verified:
            return AnonymousUser()
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, CustomUser.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Wateen Sec-WebSocket-Protocol JWT Auth
        headers = dict(scope['headers'])
        sec_protocol = headers.get(b'sec-websocket-protocol', b'').decode('utf-8')

        token = None
        if sec_protocol:
            # Protocol usually passed as: ['jwt', '<token>'] or just '<token>'
            protocols = [p.strip() for p in sec_protocol.split(',')]
            for p in protocols:
                if p != 'jwt':
                    token = p
                    break

        if token:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()

        if isinstance(scope['user'], AnonymousUser):
            # 4401 Code for Unauthorized WebSocket
            await send({"type": "websocket.close", "code": 4401})
            return

        # Add requested protocol to scope so consumer can echo it back
        scope['subprotocols'] = [token] if token else []
        return await super().__call__(scope, receive, send)
