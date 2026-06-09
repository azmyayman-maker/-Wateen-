import sys
from pathlib import Path
import os
import django

# Add project root and backend to sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
BACKEND_ROOT = str(Path(__file__).resolve().parents[1] / "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def pytest_configure(config):  # noqa: ARG001
    """Configure pytest with Django settings."""
    django.setup()
