"""
JSON Output Formatter

Generates JSON reports for infrastructure verification results.
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from .models import InfrastructureTestReport, VerificationResult


def generate_json_report(
    report: InfrastructureTestReport,
    output_path: Optional[str] = None,
) -> str:
    output_path = output_path or os.environ.get(
        "VERIFICATION_JSON_PATH", "./verification-report.json"
    )

    report_dict = report.to_dict()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)

    return output_path


def generate_component_json(
    result: VerificationResult,
    output_path: Optional[str] = None,
) -> str:
    output_path = output_path or os.environ.get(
        "VERIFICATION_JSON_PATH", f"./{result.component}-verification-report.json"
    )

    result_dict = result.to_dict()

    report = {
        "timestamp": result.timestamp,
        "overall_status": result.status.value,
        "components": {result.component: result_dict},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return output_path


def format_timestamp(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()
