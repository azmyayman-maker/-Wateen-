"""
Verification Models

Data structures for infrastructure verification results.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union


class VerificationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class CRUDStatus:
    create: bool = False
    read: bool = False
    update: bool = False
    delete: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "create": self.create,
            "read": self.read,
            "update": self.update,
            "delete": self.delete,
        }
        if self.error:
            result["error"] = self.error
        return result

    @property
    def all_passed(self) -> bool:
        return self.create and self.read and self.update and self.delete


@dataclass
class CacheOperations:
    set: bool = False
    get: bool = False
    delete: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "set": self.set,
            "get": self.get,
            "delete": self.delete,
        }
        if self.error:
            result["error"] = self.error
        return result

    @property
    def all_passed(self) -> bool:
        return self.set and self.get and self.delete


@dataclass
class PubSubStatus:
    subscribe: bool = False
    publish: bool = False
    receive: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "subscribe": self.subscribe,
            "publish": self.publish,
            "receive": self.receive,
        }
        if self.error:
            result["error"] = self.error
        return result

    @property
    def all_passed(self) -> bool:
        return self.subscribe and self.publish and self.receive


@dataclass
class VerificationResult:
    component: str
    status: VerificationStatus
    latency_ms: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    details: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "component": self.component,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 2),
            "timestamp": self.timestamp,
        }
        if self.details:
            result["details"] = self.details
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class DatabaseVerificationResult(VerificationResult):
    postgis_version: Optional[str] = None
    crud_status: Optional[CRUDStatus] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.postgis_version:
            result["postgis_version"] = self.postgis_version
        if self.crud_status:
            result["crud_status"] = self.crud_status.to_dict()
        return result


@dataclass
class CacheVerificationResult(VerificationResult):
    operations: Optional[CacheOperations] = None
    pubsub_status: Optional[PubSubStatus] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.operations:
            result["operations"] = self.operations.to_dict()
        if self.pubsub_status:
            result["pubsub_status"] = self.pubsub_status.to_dict()
        return result


@dataclass
class InfrastructureTestReport:
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    overall_status: VerificationStatus = VerificationStatus.PASS
    total_duration_ms: float = 0.0
    components: dict = field(default_factory=dict)
    summary: str = ""
    environment: Optional[dict] = None

    def add_component(
        self,
        result: Union[
            VerificationResult, DatabaseVerificationResult, CacheVerificationResult
        ],
    ) -> None:
        self.components[result.component] = result.to_dict()
        if result.status == VerificationStatus.FAIL:
            self.overall_status = VerificationStatus.FAIL
        elif (
            result.status == VerificationStatus.WARNING
            and self.overall_status != VerificationStatus.FAIL
        ):
            self.overall_status = VerificationStatus.WARNING

    def to_dict(self) -> dict:
        result = {
            "timestamp": self.timestamp,
            "overall_status": self.overall_status.value,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "components": self.components,
        }
        if self.summary:
            result["summary"] = self.summary
        if self.environment:
            result["environment"] = self.environment
        return result
