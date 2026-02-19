"""
Cache Verification Script

Verifies Redis connectivity and functionality with structured output.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis

from scripts.verification.base import BaseVerifier
from scripts.verification.config import VerificationConfig, get_config
from scripts.verification.models import (
    CacheVerificationResult,
    VerificationStatus,
    CacheOperations,
    PubSubStatus,
)
from scripts.verification.console import print_header, print_cache_result
from typing import cast


class CacheVerifier(BaseVerifier):
    def __init__(self, config: VerificationConfig | None = None):
        super().__init__(config)
        self._client: redis.Redis | None = None

    def get_component_name(self) -> str:
        return "cache"

    def _get_client(self) -> redis.Redis:
        redis_url = self.config.redis_url or "redis://localhost:6379/1"
        return redis.from_url(
            redis_url,
            socket_timeout=self.config.timeout_seconds,
            socket_connect_timeout=self.config.timeout_seconds,
        )

    def verify_operations(self, client: redis.Redis) -> CacheOperations:
        ops = CacheOperations()

        try:
            test_key = "infra_test_key"
            test_value = "infra_test_value"

            client.set(test_key, test_value, ex=10)
            ops.set = True

            retrieved = client.get(test_key)
            if retrieved and retrieved.decode("utf-8") == test_value:
                ops.get = True

            client.delete(test_key)
            ops.delete = True

        except Exception:
            pass

        return ops

    def verify_pubsub(self, client: redis.Redis) -> PubSubStatus:
        pubsub_status = PubSubStatus()
        pubsub = None

        try:
            pubsub = client.pubsub()
            channel = "test_channel"

            pubsub.subscribe(channel)
            pubsub_status.subscribe = True

            start_wait = time.time()
            subscribed = False
            while time.time() - start_wait < 2:
                message = pubsub.get_message()
                if message and message["type"] == "subscribe":
                    subscribed = True
                    break
                time.sleep(0.01)

            if not subscribed:
                pubsub_status.subscribe = False
                return pubsub_status

            message_data = "Hello Wateen"
            client.publish(channel, message_data)
            pubsub_status.publish = True

            start_wait = time.time()
            received = False
            while time.time() - start_wait < 2:
                message = pubsub.get_message()
                if message and message["type"] == "message":
                    decoded_message = message["data"].decode("utf-8")
                    if decoded_message == message_data:
                        received = True
                        break
                time.sleep(0.01)

            pubsub_status.receive = received

        except Exception:
            pass
        finally:
            if pubsub:
                try:
                    pubsub.unsubscribe()
                    pubsub.close()
                except Exception:
                    pass

        return pubsub_status

    def verify(self) -> CacheVerificationResult:
        latency_ms = 0.0
        operations = None
        pubsub_status = None
        error = None
        status = VerificationStatus.PASS
        details = []
        client = None

        try:
            client = self._get_client()

            start = time.time()
            client.ping()
            latency_ms = (time.time() - start) * 1000

            if latency_ms > self.config.latency_threshold_ms:
                if latency_ms > self.config.latency_warning_ms:
                    status = VerificationStatus.FAIL
                    error = f"Latency {latency_ms:.0f}ms exceeds threshold {self.config.latency_warning_ms}ms"
                else:
                    status = VerificationStatus.WARNING
                    details.append(
                        f"Latency {latency_ms:.0f}ms above target {self.config.latency_threshold_ms}ms"
                    )
            else:
                details.append(f"Latency {latency_ms:.0f}ms")

            operations = self.verify_operations(client)
            if operations.all_passed:
                details.append("Operations passed")
            else:
                status = VerificationStatus.FAIL
                error = "Cache operations failed"

            pubsub_status = self.verify_pubsub(client)
            if pubsub_status.all_passed:
                details.append("Pub/Sub passed")
            else:
                if status != VerificationStatus.FAIL:
                    status = VerificationStatus.WARNING
                details.append("Pub/Sub issues detected")

        except redis.TimeoutError:
            status = VerificationStatus.FAIL
            error = f"Connection timed out after {self.config.timeout_seconds}s"
            latency_ms = self.elapsed_ms()
        except redis.ConnectionError as e:
            status = VerificationStatus.FAIL
            error = f"Connection failed: {e}"
            latency_ms = self.elapsed_ms()
        except Exception as e:
            status = VerificationStatus.FAIL
            error = str(e)
            latency_ms = self.elapsed_ms()
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

        return CacheVerificationResult(
            component="cache",
            status=status,
            latency_ms=latency_ms,
            operations=operations,
            pubsub_status=pubsub_status,
            error=error,
            details=" | ".join(details) if details else "",
        )

    def print_console_output(self) -> None:
        print_header("Cache Verification")
        if self.result:
            print_cache_result(cast(CacheVerificationResult, self.result))


def main() -> int:
    config = get_config()
    verifier = CacheVerifier(config)
    return verifier.run()


if __name__ == "__main__":
    sys.exit(main())
