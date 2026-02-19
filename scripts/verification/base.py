"""
Base Verifier

Base class for infrastructure verification with timeout and exit code handling.
"""

import sys
import time
from abc import ABC, abstractmethod
from typing import Optional

from .config import VerificationConfig, get_config
from .models import VerificationResult, VerificationStatus
from .output import generate_component_json


class BaseVerifier(ABC):
    def __init__(self, config: Optional[VerificationConfig] = None):
        self.config = config or get_config()
        self.start_time: Optional[float] = None
        self.result: Optional[VerificationResult] = None

    def start_timer(self) -> None:
        self.start_time = time.time()

    def elapsed_ms(self) -> float:
        if self.start_time is None:
            return 0.0
        return (time.time() - self.start_time) * 1000

    @abstractmethod
    def verify(self) -> VerificationResult:
        pass

    def run(self) -> int:
        self.start_timer()
        try:
            self.result = self.verify()
        except Exception as e:
            self.result = VerificationResult(
                component=self.get_component_name(),
                status=VerificationStatus.FAIL,
                latency_ms=self.elapsed_ms(),
                error=str(e),
                details=f"Verification failed with exception: {e}",
            )

        return self._handle_output()

    def _handle_output(self) -> int:
        if self.result is None:
            return 1

        if self.config.should_output_console():
            self.print_console_output()

        if self.config.should_output_json():
            json_path = generate_component_json(self.result, self.config.json_path)
            if self.config.should_output_console():
                print(f"Report: {json_path}")

        if self.result.status == VerificationStatus.FAIL:
            return 1
        return 0

    @abstractmethod
    def get_component_name(self) -> str:
        pass

    @abstractmethod
    def print_console_output(self) -> None:
        pass
