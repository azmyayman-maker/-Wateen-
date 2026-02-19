"""
Configuration Loader

Loads environment variables for verification scripts.

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    REDIS_URL: Redis connection string (default: redis://localhost:6379/1)
    VERIFICATION_TIMEOUT: Connection timeout in seconds (default: 5)
    VERIFICATION_OUTPUT: Output format - console, json, or both (default: both)
    VERIFICATION_JSON_PATH: Path for JSON output file (default: ./verification-report.json)
    VERIFICATION_LATENCY_THRESHOLD: Latency threshold in ms for pass (default: 100)
    VERIFICATION_LATENCY_WARNING: Latency threshold in ms for warning (default: 200)

Example:
    >>> from scripts.verification.config import get_config
    >>> config = get_config()
    >>> print(config.timeout_seconds)
    5
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class VerificationConfig:
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    timeout_seconds: int = 5
    output_format: str = "both"
    json_path: str = "./verification-report.json"
    latency_threshold_ms: int = 100
    latency_warning_ms: int = 200

    @classmethod
    def from_env(cls) -> "VerificationConfig":
        return cls(
            database_url=os.environ.get("DATABASE_URL"),
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/1"),
            timeout_seconds=int(os.environ.get("VERIFICATION_TIMEOUT", "5")),
            output_format=os.environ.get("VERIFICATION_OUTPUT", "both"),
            json_path=os.environ.get(
                "VERIFICATION_JSON_PATH", "./verification-report.json"
            ),
            latency_threshold_ms=int(
                os.environ.get("VERIFICATION_LATENCY_THRESHOLD", "100")
            ),
            latency_warning_ms=int(
                os.environ.get("VERIFICATION_LATENCY_WARNING", "200")
            ),
        )

    def should_output_console(self) -> bool:
        return self.output_format in ("console", "both")

    def should_output_json(self) -> bool:
        return self.output_format in ("json", "both")


def get_config() -> VerificationConfig:
    return VerificationConfig.from_env()
