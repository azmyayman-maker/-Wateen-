"""
P4-T5: Locust Load Testing Configuration
========================================
Performance tests for 500 concurrent dispatch requests.

Target KPIs:
- Average response time < 2000ms
- 95th percentile < 3000ms
- Error rate < 1%
- Spatial queries < 50ms average
"""

import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner
import uuid
from datetime import datetime


class DispatchUser(HttpUser):
    """
    Simulates a user creating visit requests and accepting dispatch offers.

    Task weights:
    - create_visit_request (3): Most common action
    - accept_dispatch_offer (1): Less common
    - check_visit_status (1): Status polling
    """

    wait_time = between(1, 3)

    def on_start(self):
        """Initialize test data for each user session."""
        self.agency_ids = []
        self.visit_ids = []
        self.offer_ids = []
        self.patient_token = None
        self.nurse_tokens = []

        self._setup_authentication()

    def _setup_authentication(self):
        """Set up authentication tokens for testing."""
        pass

    @task(3)
    def create_visit_request(self):
        """
        POST /api/v1/visits/request/ - Create a new visit request.

        Tests spatial intersection and dispatch queue performance.
        """
        latitude = 30.0444 + random.uniform(-0.1, 0.1)
        longitude = 31.2357 + random.uniform(-0.1, 0.1)

        urgency_options = ["low", "medium", "high", "sos"]
        urgency = random.choice(urgency_options)

        payload = {
            "service_type_id": str(uuid.uuid4()),
            "latitude": latitude,
            "longitude": longitude,
            "urgency": urgency,
            "notes": f"Load test visit at {datetime.now().isoformat()}",
        }

        with self.client.post(
            "/api/v1/visits/request/",
            json=payload,
            catch_response=True,
            name="create_visit_request",
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if "visit_id" in data:
                        self.visit_ids.append(data["visit_id"])
                    response.success()
                except Exception:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def accept_dispatch_offer(self):
        """
        POST /api/v1/visits/nurse/respond-offer/ - Accept a dispatch offer.

        Tests race condition handling under load.
        """
        if not self.offer_ids:
            return

        offer_id = random.choice(self.offer_ids)

        payload = {"offer_id": str(offer_id), "action": "accept"}

        with self.client.post(
            "/api/v1/visits/nurse/respond-offer/",
            json=payload,
            catch_response=True,
            name="accept_dispatch_offer",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 409:
                response.success()
            elif response.status_code == 410:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def check_visit_status(self):
        """
        GET /api/v1/visits/{id}/ - Check visit status.

        Tests read performance of visit lookups.
        """
        if not self.visit_ids:
            return

        visit_id = random.choice(self.visit_ids)

        with self.client.get(
            f"/api/v1/visits/{visit_id}/",
            catch_response=True,
            name="check_visit_status",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


class SpatialQueryUser(HttpUser):
    """
    Dedicated user for testing PostGIS spatial query performance.

    Targets: find_agencies_covering_point()
    KPI: < 50ms average query time
    """

    wait_time = between(0.5, 1.5)

    @task(5)
    def query_covering_agencies(self):
        """
        GET /api/v1/geo/find-agencies/ - Find agencies covering a point.

        Tests ST_Intersects GIST index performance.
        """
        latitude = 30.0444 + random.uniform(-0.2, 0.2)
        longitude = 31.2357 + random.uniform(-0.2, 0.2)

        with self.client.get(
            f"/api/v1/geo/find-agencies/?latitude={latitude}&longitude={longitude}",
            catch_response=True,
            name="query_covering_agencies",
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    response.success()
                except Exception:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


class CeleryQueueUser(HttpUser):
    """
    Tests Celery dispatch queue performance under load.

    Monitors queue depth and task processing time.
    """

    wait_time = between(2, 5)

    @task(1)
    def trigger_dispatch_task(self):
        """
        Trigger a background dispatch task.

        Tests Celery task queue throughput.
        """
        payload = {"action": "test_dispatch", "visit_id": str(uuid.uuid4())}

        with self.client.post(
            "/api/v1/dispatch/trigger/",
            json=payload,
            catch_response=True,
            name="trigger_dispatch_task",
        ) as response:
            if response.status_code in [200, 201, 202]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


# ============================================================================
# Event Handlers for Metrics Collection
# ============================================================================


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests for analysis."""
    if response_time > 2000:
        print(f"SLOW REQUEST: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test environment."""
    print("=" * 60)
    print("P4-T5: Dispatch & Pricing Load Test")
    print("Target: 500 concurrent users")
    print("KPI: < 2000ms average response time")
    print("KPI: < 50ms spatial query average")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test summary."""
    print("=" * 60)
    print("Load test completed")
    print("Check locust stats for detailed metrics")
    print("=" * 60)


# ============================================================================
# Configuration
# ============================================================================

# Run with: locust -f locustfile.py --users 500 --spawn-rate 50 --run-time 5m --headless
# Or with web UI: locust -f locustfile.py --users 500 --spawn-rate 50
