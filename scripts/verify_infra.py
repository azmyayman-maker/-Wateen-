"""
Comprehensive Infrastructure Verification Script

Runs all infrastructure verification checks and generates aggregated report.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from typing import Any, Tuple
from scripts.verification.config import VerificationConfig, get_config
from scripts.verification.models import (
    InfrastructureTestReport,
    VerificationStatus,
    DatabaseVerificationResult,
    CacheVerificationResult,
)
from scripts.verification.console import print_header, print_footer, print_result
from scripts.verification.output import generate_json_report


def run_database_verification() -> Tuple[int, Any]:
    from scripts.verify_local_db import DatabaseVerifier

    config = get_config()
    verifier = DatabaseVerifier(config)
    exit_code = verifier.run()
    return exit_code, verifier.result


def run_cache_verification() -> Tuple[int, Any]:
    from scripts.verify_local_redis import CacheVerifier

    config = get_config()
    verifier = CacheVerifier(config)
    exit_code = verifier.run()
    return exit_code, verifier.result


def main() -> int:
    config = get_config()

    if config.should_output_console():
        print_header("Infrastructure Verification")

    start_time = time.time()
    report = InfrastructureTestReport()

    db_exit_code = 0
    cache_exit_code = 0

    if config.should_output_console():
        print("\n[Database Verification]")

    try:
        db_exit_code, db_result = run_database_verification()
        if db_result:
            report.add_component(db_result)
            if config.should_output_console():
                print_result(db_result)
    except Exception as e:
        db_exit_code = 1
        db_result = DatabaseVerificationResult(
            component="database",
            status=VerificationStatus.FAIL,
            latency_ms=0.0,
            error=str(e),
            details="Verification failed with exception",
        )
        report.add_component(db_result)
        if config.should_output_console():
            print(f"Database verification failed: {e}")

    if config.should_output_console():
        print("\n[Cache Verification]")

    try:
        cache_exit_code, cache_result = run_cache_verification()
        if cache_result:
            report.add_component(cache_result)
            if config.should_output_console():
                print_result(cache_result)
    except Exception as e:
        cache_exit_code = 1
        cache_result = CacheVerificationResult(
            component="cache",
            status=VerificationStatus.FAIL,
            latency_ms=0.0,
            error=str(e),
            details="Verification failed with exception",
        )
        report.add_component(cache_result)
        if config.should_output_console():
            print(f"Cache verification failed: {e}")

    total_duration_ms = (time.time() - start_time) * 1000
    report.total_duration_ms = total_duration_ms

    if config.should_output_json():
        json_path = generate_json_report(report, config.json_path)
    else:
        json_path = config.json_path

    if config.should_output_console():
        print_footer(
            report.overall_status,
            total_duration_ms,
            json_path if config.should_output_json() else None,
        )

    if report.overall_status == VerificationStatus.FAIL:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
