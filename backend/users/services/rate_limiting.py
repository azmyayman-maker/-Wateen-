"""
Rate Limiting Service for Wateen B2B2C Platform.

Implements Redis-backed Token Bucket rate limiting for:
- Preventing SMS/Email bombing in invitation flows
- Enforcing SaaS tier limits per agency
- Protecting public endpoints from abuse

Design Decision (from research.md):
- Choice: Redis-backed "Token Bucket" via `django-redis`
- Rationale: High-performance, distributed rate limiting essential for 
  multi-tenant B2B2C environment
- Implementation: Rolling window counter with TTL for "6 invitations per hour per agency"
"""

from abc import ABC, abstractmethod
from typing import Optional

from django.core.cache import cache


class BaseRateLimiter(ABC):
    """
    Abstract base class for rate limiting implementations.
    
    Provides a common interface for different rate limiting strategies.
    """

    @abstractmethod
    def is_allowed(self, key: str) -> bool:
        """
        Check if the request is allowed under the rate limit.
        
        Args:
            key: Unique identifier for the rate limit bucket (e.g., "invite:{agency_id}")
            
        Returns:
            True if the request is allowed, False if rate limit exceeded
        """
        pass

    @abstractmethod
    def get_remaining(self, key: str) -> int:
        """
        Get the number of remaining requests in the current window.
        
        Args:
            key: Unique identifier for the rate limit bucket
            
        Returns:
            Number of remaining requests (0 if exceeded)
        """
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """
        Reset the rate limit counter for a given key.
        
        Args:
            key: Unique identifier for the rate limit bucket
        """
        pass


class TokenBucketRateLimiter(BaseRateLimiter):
    """
    Token Bucket Rate Limiter using Redis.
    
    Implements a sliding window counter with TTL for distributed rate limiting.
    Perfect for preventing SMS/Email bombing in multi-tenant environments.
    
    Usage:
        limiter = TokenBucketRateLimiter(
            max_requests=6,
            window_seconds=3600,  # 1 hour
            prefix="invite"
        )
        
        if limiter.is_allowed(str(agency_id)):
            # Proceed with invitation
            pass
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        prefix: str = "ratelimit"
    ):
        """
        Initialize the Token Bucket Rate Limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
            prefix: Cache key prefix for namespacing
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix

        # Determine cache timeout - add buffer to prevent early expiration
        self._cache_timeout = window_seconds + 60

    def _get_cache_key(self, key: str) -> str:
        """Build the full cache key with prefix."""
        return f"{self.prefix}:{key}"

    def is_allowed(self, key: str) -> bool:
        """
        Check if the request is allowed and increment the counter atomically.
        
        Uses Redis INCR for atomic increment to prevent TOCTOU race conditions.
        Handles missing keys by initializing with cache.set() on first access.
        
        Args:
            key: Unique identifier (e.g., agency_id for invitation limits)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        cache_key = self._get_cache_key(key)

        try:
            try:
                # Atomic increment — prevents TOCTOU race condition
                new_count = cache.incr(cache_key)
            except ValueError:
                # Key doesn't exist — use cache.add() for atomic initialization.
                # cache.add() is a no-op if another thread inserted first,
                # preventing the race where two threads both set count to 1.
                if cache.add(cache_key, 1, self.window_seconds):
                    new_count = 1
                else:
                    # Another thread won the race — safely increment
                    new_count = cache.incr(cache_key)

            return new_count <= self.max_requests
        except Exception:
            # On genuine cache failure (Redis down), allow the request (fail-open)
            return True

    def get_remaining(self, key: str) -> int:
        """
        Get the number of remaining requests in the current window.
        
        Args:
            key: Unique identifier for the rate limit bucket
            
        Returns:
            Number of remaining requests (0 if exceeded or cache error)
        """
        cache_key = self._get_cache_key(key)
        current = cache.get(cache_key, 0)
        return max(0, self.max_requests - current)

    def reset(self, key: str) -> None:
        """
        Reset the rate limit counter for a given key.
        
        Args:
            key: Unique identifier for the rate limit bucket
        """
        cache_key = self._get_cache_key(key)
        cache.delete(cache_key)

    def get_reset_time(self, key: str) -> Optional[int]:
        """
        Get the Unix timestamp when the rate limit will reset.
        
        Args:
            key: Unique identifier for the rate limit bucket
            
        Returns:
            Unix timestamp of reset time, or None if no limit active
        """
        cache_key = self._get_cache_key(key)
        ttl = cache.ttl(cache_key)

        if ttl is None or ttl < 0:
            return None

        import time
        return int(time.time()) + ttl


class InvitationRateLimiter:
    """
    Rate limiter specifically for nurse invitation flow.
    
    Enforces:
    - 6 invitations per hour per agency (burst protection)
    - Prevents SMS/Email bombing attacks
    
    Usage:
        limiter = InvitationRateLimiter()
        
        if not limiter.is_allowed(agency_id):
            return Response({
                "detail": "Invitation limit reached. Please try again later.",
                "code": "rate_limited"
            }, status=429)
    """

    # Rate limit configuration
    MAX_INVITATIONS_PER_HOUR = 6
    WINDOW_SECONDS = 3600  # 1 hour
    CACHE_PREFIX = "invite_limit"

    def __init__(self):
        """Initialize the invitation rate limiter."""
        self._limiter = TokenBucketRateLimiter(
            max_requests=self.MAX_INVITATIONS_PER_HOUR,
            window_seconds=self.WINDOW_SECONDS,
            prefix=self.CACHE_PREFIX
        )

    def is_allowed(self, agency_id: str) -> bool:
        """
        Check if the agency can send another invitation.
        
        Args:
            agency_id: UUID of the agency
            
        Returns:
            True if invitation is allowed, False if limit exceeded
        """
        return self._limiter.is_allowed(str(agency_id))

    def get_remaining(self, agency_id: str) -> int:
        """
        Get remaining invitations for the agency in current window.
        
        Args:
            agency_id: UUID of the agency
            
        Returns:
            Number of remaining invitations
        """
        return self._limiter.get_remaining(str(agency_id))

    def reset(self, agency_id: str) -> None:
        """
        Reset the rate limit for an agency (admin use only).
        
        Args:
            agency_id: UUID of the agency
        """
        self._limiter.reset(str(agency_id))

    def get_reset_time(self, agency_id: str) -> int | None:
        """
        Get the Unix timestamp when the rate limit will reset.
        
        Args:
            agency_id: UUID of the agency
            
        Returns:
            Unix timestamp of reset time, or None if no limit active
        """
        return self._limiter.get_reset_time(str(agency_id))


import functools


@functools.lru_cache(maxsize=1)
def get_invitation_rate_limiter() -> InvitationRateLimiter:
    """
    Get the singleton invitation rate limiter instance.
    
    Thread-safe via lru_cache's internal lock.
    
    Returns:
        InvitationRateLimiter instance
    """
    return InvitationRateLimiter()
