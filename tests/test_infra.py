
import pytest
import os
from django.db import connection
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@pytest.mark.django_db
def test_postgres_connection_and_extension():
    """Verify primary database connection and PostGIS extension."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        assert row[0] == 1, "Database connection failed"
        
        cursor.execute("SELECT postgis_version();")
        version_row = cursor.fetchone()
        assert version_row is not None, "PostGIS extension not found"
        print(f"PostGIS Version: {version_row[0]}")

def test_redis_cache_connection():
    """Verify Redis cache connection."""
    cache.set('infra_test_key', 'infra_test_value', 10)
    value = cache.get('infra_test_key')
    assert value == 'infra_test_value', "Redis cache set/get failed"
    cache.delete('infra_test_key')

@pytest.mark.asyncio
async def test_redis_channel_layer():
    """Verify Redis Channel Layer (Async)."""
    channel_layer = get_channel_layer()
    channel_name = "infra_test_channel"
    message = {"type": "test.message", "text": "hello infra"}
    
    await channel_layer.send(channel_name, message)
    received = await channel_layer.receive(channel_name)
    
    assert received['text'] == message['text'], "Channel layer send/receive failed"
