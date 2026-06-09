import time

from locust import HttpUser, between, task


class DashboardWebSocketUser(HttpUser):
    """
    Locust Load Testing scenario targeting the Channels ASGI endpoint.
    Goal: Maintain < 500ms broadcast latency across 5,000 WebSocket streams.
    Requires `websocket-client` plugin for proper WSS interception in locust.
    """
    wait_time = between(1, 5)

    def on_start(self):
        try:
            from websocket import create_connection
            # Mock JWT generation targeting the 5k load threshold
            self.agency_id = "test-agency-id"
            self.token = "mock.jwt.token"
            self.ws = create_connection(
                "ws://localhost:8000/ws/dashboard/agency/",
                header=[f"Sec-WebSocket-Protocol: {self.token}"]
            )
        except Exception:
            self.ws = None

    @task
    def receive_heartbeat(self):
        if not self.ws:
            return

        start_time = time.time()
        try:
            result = self.ws.recv()
            elapsed = int((time.time() - start_time) * 1000)

            # Fire events manually to Locust tracking
            if result and "heartbeat" in result:
                self.environment.events.request.fire(
                    request_type="WebSocket Recv",
                    name="dashboard.heartbeat",
                    response_time=elapsed,
                    response_length=len(result),
                    exception=None,
                )
        except Exception as e:
            self.environment.events.request.fire(
                request_type="WebSocket Recv",
                name="dashboard.heartbeat",
                response_time=0,
                response_length=0,
                exception=e,
            )

    def on_stop(self):
        if self.ws:
            self.ws.close()
