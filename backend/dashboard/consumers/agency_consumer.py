import asyncio
import json
from datetime import datetime, timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from dashboard.services.metrics_engine import calculate_agency_metrics
from dashboard.utils.cache_shield import CacheShield
from dashboard.utils.connection_tracker import ConnectionTracker


class DashboardMetricsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated or self.user.role != 'AGENCY_ADMIN':
            await self.close(code=4401)
            return

        self.agency_id = str(self.user.agency_profile.id)

        # Enforce rate capping using precise ZSET checking
        if not ConnectionTracker.add_connection(self.agency_id, self.channel_name):
            await self.close(code=1008) # Policy Violation
            return

        self.room_group_name = f'agency_{self.agency_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Echo the requested Sec-WebSocket-Protocol token
        subprotocols = self.scope.get('subprotocols', [])
        if subprotocols:
            await self.accept(subprotocol=subprotocols[0])
        else:
            await self.accept()

        self.heartbeat_task = asyncio.create_task(self.broadcast_heartbeat_loop())

    async def disconnect(self, close_code):
        if hasattr(self, 'agency_id'):
            ConnectionTracker.remove_connection(self.agency_id)
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        # Socket is strictly demand-driven and read-only. Unprovoked incoming payloads drop connection.
        if text_data or bytes_data:
            await self.close(code=1008)

    async def broadcast_heartbeat_loop(self):
        try:
            while True:
                # Update TTL mapping for this channel to prevent zombie cleaning
                ConnectionTracker.heartbeat_connection(self.agency_id, self.channel_name)

                metrics = CacheShield.get_agency_metrics(self.agency_id)
                if not metrics:
                    # Cache Miss - Lock is atomic
                    with CacheShield.lock_agency(self.agency_id) as acquired:
                        if acquired:
                            metrics = await database_sync_to_async(calculate_agency_metrics)(self.agency_id)
                            CacheShield.set_agency_metrics(self.agency_id, metrics)
                        else:
                            await asyncio.sleep(0.5)
                            continue

                if metrics:
                    payload = {
                        "type": "dashboard.heartbeat",
                        "agency_id": self.agency_id,
                        "data": {
                            "metrics": metrics,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    }
                    await self.send(text_data=json.dumps(payload))

                await asyncio.sleep(10)
        except asyncio.CancelledError:
            # Graceful shutdown achieved. Prevent log pollution.
            pass
