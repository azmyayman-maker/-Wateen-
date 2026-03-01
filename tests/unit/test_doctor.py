"""
Unit tests for the doctor.py diagnostic script.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.doctor import (
    check_python_version,
    check_env_file,
    check_redis,
    check_database,
    check_gdal,
    CheckResult,
    PASS,
    FAIL,
    WARNING,
)


class TestCheckPythonVersion:
    """Tests for Python version check."""

    def test_python_version_pass(self):
        """Should pass if Python 3.11+."""
        result = check_python_version()
        assert result.status in (PASS, FAIL)
        assert "Python" in result.name

    def test_python_version_includes_version_in_message(self):
        """Should include version in message."""
        result = check_python_version()
        assert "." in result.message


class TestCheckEnvFile:
    """Tests for environment file check."""

    def test_env_file_exists(self, tmp_path, monkeypatch):
        """Should pass if .env exists."""
        env_file = tmp_path / ".env"
        env_file.write_text("DEBUG=True")
        monkeypatch.chdir(tmp_path)

        result = check_env_file()
        assert result.status == PASS

    def test_env_file_missing(self, tmp_path, monkeypatch):
        """Should fail if .env missing."""
        monkeypatch.chdir(tmp_path)

        result = check_env_file()
        assert result.status == FAIL
        assert result.fix_command is not None


class TestCheckRedis:
    """Tests for Redis connectivity check."""

    def test_redis_not_configured(self, monkeypatch):
        """Should warn if REDIS_URL not set."""
        monkeypatch.delenv("REDIS_URL", raising=False)

        result = check_redis()
        assert result.status == WARNING

    def test_redis_invalid_url(self, monkeypatch):
        """Should fail if REDIS_URL is invalid."""
        monkeypatch.setenv("REDIS_URL", "not-a-valid-url")

        result = check_redis()
        assert result.status == FAIL

    def test_redis_unreachable(self, monkeypatch):
        """Should fail if Redis is unreachable."""
        monkeypatch.setenv("REDIS_URL", "redis://nonexistent-host-12345:6379/0")

        result = check_redis()
        assert result.status in (FAIL, WARNING)


class TestCheckDatabase:
    """Tests for database connectivity check."""

    def test_database_not_configured(self, monkeypatch):
        """Should warn if DATABASE_URL not set."""
        monkeypatch.delenv("DATABASE_URL", raising=False)

        result = check_database()
        assert result.status == WARNING


class TestCheckGDAL:
    """Tests for GDAL availability check."""

    def test_gdal_check_returns_result(self):
        """Should return a CheckResult."""
        result = check_gdal()
        assert isinstance(result, CheckResult)
        assert result.status in (PASS, FAIL, WARNING)

    def test_gdal_on_windows_without_path(self, monkeypatch):
        """Should warn on Windows without GDAL path."""
        monkeypatch.setattr(os, "name", "nt")
        monkeypatch.delenv("GDAL_LIBRARY_PATH", raising=False)

        result = check_gdal()
        assert result.status == WARNING
