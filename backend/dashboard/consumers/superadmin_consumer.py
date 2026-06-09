import asyncio
import json
from datetime import datetime, timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection

from dashboard.services.superadmin_engine import get_fuzzed_nationwide_heatmap


class SuperAdminCommandConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated or self.user.role != 'SUPERADMIN':
            await self.close(code=4401)
            return

        # SuperAdmin has no agency limits, but joins a global group
        self.room_group_name = 'superadmin_national'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        subprotocols = self.scope.get('subprotocols', [])
        if subprotocols:
            await self.accept(subprotocol=subprotocols[0])
        else:
            await self.accept()

        self.heartbeat_task = asyncio.create_task(self.broadcast_loop())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()

    async def broadcast_loop(self):
        try:
            while True:
                # Native Geospatial Fuzzing
                heatmap_data = await database_sync_to_async(get_fuzzed_nationwide_heatmap)()

                # Redis Infrastructure Health (memory latency check)
                try:
                    redis_conn = get_redis_connection("default")
                    info = redis_conn.info('memory')
                    used_memory_human = info.get('used_memory_human', 'N/A')
                except Exception:
                    used_memory_human = "Error"

                payload = {
                    "type": "dashboard.superadmin",
                    "data": {
                        "heatmap": heatmap_data,
                        "infrastructure": {
                            "redis_used_memory": used_memory_human
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
                await self.send(text_data=json.dumps(payload))
                await asyncio.sleep(15) # SuperAdmin payload evaluates every 15s to reduce load
        except asyncio.CancelledError:
            # Silence expected asynchronous termination behavior
            pass
