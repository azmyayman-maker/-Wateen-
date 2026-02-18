"""
Django management command to test Redis Cloud connectivity.

This command tests both cache and channel layer connectivity to Redis Cloud
and outputs the results. It's used to verify the Redis Cloud integration
is working correctly.

Usage:
    python manage.py test_redis
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test Redis Cloud connectivity for cache and channel layers'

    def handle(self, *args, **options):
        self.stdout.write("Testing Redis Cloud connectivity...")
        
        # Get Redis URL (masked for security)
        redis_url = os.environ.get('REDIS_URL', 'Not configured')
        masked_url = self._mask_url(redis_url)
        self.stdout.write(f"Redis URL: {masked_url}")
        
        # Test cache connection
        cache_ok = self._test_cache()
        
        # Test channel layer
        channel_ok = self._test_channel_layer() if cache_ok else False
        
        # Report results
        if cache_ok and channel_ok:
            self.stdout.write(
                self.style.SUCCESS("Redis Connected Successfully")
            )
        else:
            self.stdout.write(
                self.style.ERROR("Redis connection failed")
            )
            exit(1)

    def _mask_url(self, url):
        """Mask password in Redis URL for security."""
        if '://' in url and '@' in url:
            # redis://:password@host:port/db
            parts = url.split('://')
            if len(parts) == 2:
                protocol = parts[0]
                rest = parts[1]
                if '@' in rest:
                    auth, host = rest.split('@', 1)
                    return f"{protocol}://***@{host}"
        return url

    def _test_cache(self):
        """Test cache connectivity."""
        try:
            # Test set
            test_key = 'redis_test_key'
            test_value = 'redis_test_value'
            cache.set(test_key, test_value, 10)
            
            # Test get
            retrieved = cache.get(test_key)
            if retrieved != test_value:
                self.stdout.write(
                    self.style.ERROR(f"Cache: FAILED - Value mismatch (expected '{test_value}', got '{retrieved}')")
                )
                return False
            
            # Test delete
            cache.delete(test_key)
            
            self.stdout.write(self.style.SUCCESS("Cache: OK"))
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Cache: FAILED - {str(e)}")
            )
            return False

    def _test_channel_layer(self):
        """Test channel layer connectivity."""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # Test send/receive
            test_channel = 'test_channel'
            test_message = {'type': 'test.message', 'text': 'hello'}
            
            async_to_sync(channel_layer.send)(test_channel, test_message)
            received = async_to_sync(channel_layer.receive)(test_channel)
            
            if received != test_message:
                self.stdout.write(
                    self.style.ERROR(f"Channel Layer: FAILED - Message mismatch")
                )
                return False
            
            self.stdout.write(self.style.SUCCESS("Channel Layer: OK"))
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Channel Layer: FAILED - {str(e)}")
            )
            return False
