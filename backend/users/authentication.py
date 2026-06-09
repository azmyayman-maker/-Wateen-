from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads the token from an HttpOnly cookie
    if it's not present in the Authorization header.
    """
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            # Fallback to cookie
            raw_token = request.COOKIES.get(getattr(settings, 'JWT_AUTH_COOKIE', 'access_token'))
            if raw_token is not None:
                raw_token = raw_token.encode('utf-8')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
