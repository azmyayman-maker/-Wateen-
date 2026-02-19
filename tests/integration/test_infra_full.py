"""
Full Infrastructure Integration Tests

Tests the comprehensive verification suite with structured output.
"""

import json
import os
import pytest
import tempfile
from pathlib import Path


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Clean environment variables before and after each test."""
    monkeypatch.delenv("VERIFICATION_OUTPUT", raising=False)
    monkeypatch.delenv("VERIFICATION_JSON_PATH", raising=False)
    yield


@pytest.fixture
def temp_json_path():
    """Create a temporary JSON file path for testing. Cleans up file and env vars after test."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name

    yield temp_path

    # Clean up temp file, ignoring if already deleted
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass

    # Clean up environment variables
    os.environ.pop("VERIFICATION_OUTPUT", None)
    os.environ.pop("VERIFICATION_JSON_PATH", None)


@pytest.mark.django_db
def test_database_verification_produces_json(temp_json_path, monkeypatch):
    monkeypatch.setenv("VERIFICATION_OUTPUT", "json")
    monkeypatch.setenv("VERIFICATION_JSON_PATH", temp_json_path)

    from scripts.verify_local_db import DatabaseVerifier
    from scripts.verification.config import get_config

    config = get_config()
    verifier = DatabaseVerifier(config)
    exit_code = verifier.run()

    assert os.path.exists(temp_json_path), "JSON report was not created"

    with open(temp_json_path, "r") as f:
        report = json.load(f)

    assert "timestamp" in report
    assert "overall_status" in report
    assert "components" in report
    assert "database" in report["components"]

    db_result = report["components"]["database"]
    assert db_result["component"] == "database"
    assert "status" in db_result
    assert "latency_ms" in db_result

    if db_result["status"] == "pass":
        assert exit_code == 0
    else:
        assert exit_code == 1


def test_cache_verification_produces_json(temp_json_path, monkeypatch):
    monkeypatch.setenv("VERIFICATION_OUTPUT", "json")
    monkeypatch.setenv("VERIFICATION_JSON_PATH", temp_json_path)

    from scripts.verify_local_redis import CacheVerifier
    from scripts.verification.config import get_config

    config = get_config()
    verifier = CacheVerifier(config)
    exit_code = verifier.run()

    assert os.path.exists(temp_json_path), "JSON report was not created"

    with open(temp_json_path, "r") as f:
        report = json.load(f)

    assert "timestamp" in report
    assert "overall_status" in report
    assert "components" in report
    assert "cache" in report["components"]

    cache_result = report["components"]["cache"]
    assert cache_result["component"] == "cache"
    assert "status" in cache_result
    assert "latency_ms" in cache_result

    if cache_result["status"] == "pass":
        assert exit_code == 0
    else:
        assert exit_code == 1


@pytest.mark.django_db
def test_comprehensive_verification_produces_json(temp_json_path, monkeypatch):
    monkeypatch.setenv("VERIFICATION_OUTPUT", "json")
    monkeypatch.setenv("VERIFICATION_JSON_PATH", temp_json_path)

    from scripts.verify_infra import main

    exit_code = main()

    assert os.path.exists(temp_json_path), "JSON report was not created"

    with open(temp_json_path, "r") as f:
        report = json.load(f)

    assert "timestamp" in report
    assert "overall_status" in report
    assert "total_duration_ms" in report
    assert "components" in report

    assert "database" in report["components"]
    assert "cache" in report["components"]

    db_result = report["components"]["database"]
    assert db_result["component"] == "database"
    assert "status" in db_result
    assert "latency_ms" in db_result

    cache_result = report["components"]["cache"]
    assert cache_result["component"] == "cache"
    assert "status" in cache_result
    assert "latency_ms" in cache_result

    if report["overall_status"] == "pass":
        assert exit_code == 0
    else:
        assert exit_code == 1

<<<<<<< HEAD

@pytest.mark.django_db
def test_json_schema_validation(temp_json_path, monkeypatch):
    monkeypatch.setenv("VERIFICATION_OUTPUT", "json")
    monkeypatch.setenv("VERIFICATION_JSON_PATH", temp_json_path)
=======
def test_json_schema_validation(temp_json_path):
    os.environ["VERIFICATION_OUTPUT"] = "json"
    os.environ["VERIFICATION_JSON_PATH"] = temp_json_path
>>>>>>> d1caa4fffb9e080b683aa4ba6547a502e7da2b1d

    from scripts.verify_infra import main

    main()

    with open(temp_json_path, "r") as f:
        report = json.load(f)

    required_fields = ["timestamp", "overall_status", "total_duration_ms", "components"]
    for field in required_fields:
        assert field in report, f"Missing required field: {field}"

    assert report["overall_status"] in ["pass", "fail", "warning"]
    assert isinstance(report["total_duration_ms"], (int, float))
    assert isinstance(report["components"], dict)
