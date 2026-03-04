"""
Mock Payment Webhook Module

T047: Contains validation and helper functions for mock payment webhook.
Only for testing purposes - disabled in production.
"""

from django.conf import settings
from django.http import HttpRequest


def validate_mock_token(request: HttpRequest) -> bool:
    """
    Validate the mock webhook token.

    Only allows requests when DEBUG=True and X-Mock-Token header matches.

    Args:
        request: The HTTP request object

    Returns:
        True if token is valid and DEBUG mode is enabled
    """
    if not settings.DEBUG:
        return False

    token = request.headers.get("X-Mock-Token")
    expected_token = (
        settings.SECRET_KEY[:20] if settings.SECRET_KEY else "dev-only-token"
    )

    return token == expected_token


def get_mock_token() -> str:
    """
    Get the expected mock token for testing.

    Returns:
        The mock token that should be sent in X-Mock-Token header
    """
    return settings.SECRET_KEY[:20] if settings.SECRET_KEY else "dev-only-token"
