"""
Infrastructure Verification Module

Provides structured verification of PostgreSQL/PostGIS and Redis infrastructure.
"""

from .models import (
    VerificationStatus,
    VerificationResult,
    DatabaseVerificationResult,
    CacheVerificationResult,
    InfrastructureTestReport,
    CRUDStatus,
    CacheOperations,
    PubSubStatus,
)
from .config import VerificationConfig, get_config
from .base import BaseVerifier
from .console import (
    print_header,
    print_footer,
    print_result,
    print_database_result,
    print_cache_result,
)
from .output import generate_json_report, generate_component_json

__all__ = [
    "VerificationStatus",
    "VerificationResult",
    "DatabaseVerificationResult",
    "CacheVerificationResult",
    "InfrastructureTestReport",
    "CRUDStatus",
    "CacheOperations",
    "PubSubStatus",
    "VerificationConfig",
    "get_config",
    "BaseVerifier",
    "print_header",
    "print_footer",
    "print_result",
    "print_database_result",
    "print_cache_result",
    "generate_json_report",
    "generate_component_json",
]
