#!/usr/bin/env python
"""
Wateen Doctor Script

Diagnoses and reports environment configuration issues.
Run this script to check your development environment setup.

Usage:
    python scripts/doctor.py
"""

import os
import sys
import platform


def check_python_version():
    """Check Python version is 3.11+."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (need 3.11+)"


def check_gdal():
    """Check if GDAL is installed and configured."""
    # Check if GDAL_LIBRARY_PATH is set
    gdal_path = os.environ.get("GDAL_LIBRARY_PATH")
    if gdal_path:
        if os.path.exists(gdal_path):
            return True, f"GDAL configured at {gdal_path}"
        return False, f"GDAL_LIBRARY_PATH set but file not found: {gdal_path}"
    
    # Try to import GDAL
    try:
        from osgeo import gdal
        version = gdal.__version__
        return True, f"GDAL {version} (auto-detected)"
    except ImportError:
        pass
    
    # On Windows, check common paths
    if platform.system() == "Windows":
        common_paths = [
            r"C:\OSGeo4W\bin\gdal304.dll",
            r"C:\OSGeo4W\bin\gdal303.dll",
            r"C:\OSGeo4W\bin\gdal302.dll",
            r"C:\Program Files\QGIS 3.28\bin\gdal304.dll",
            r"C:\Program Files\QGIS 3.34\bin\gdal304.dll",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return False, f"GDAL found at {path} but not loaded. Set GDAL_LIBRARY_PATH={path}"
    
    return False, "GDAL not found. Install OSGeo4W or run in Docker."


def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return False, ".env file not found"
    
    # Read and check required variables
    required_vars = ["SECRET_KEY", "DATABASE_URL", "REDIS_URL"]
    found = []
    missing = []
    
    with open(env_path, "r") as f:
        content = f.read()
    
    for var in required_vars:
        if f"{var}=" in content:
            found.append(var)
        else:
            missing.append(var)
    
    if not missing:
        return True, f".env found with all required variables: {', '.join(found)}"
    return False, f".env missing: {', '.join(missing)}"


def check_database_url():
    """Check DATABASE_URL format."""
    from urllib.parse import urlparse
    
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Try loading from .env
        try:
            from decouple import config
            database_url = config("DATABASE_URL", default="")
        except Exception:
            pass
    
    if not database_url:
        return False, "DATABASE_URL not configured"
    
    # Check format
    if database_url.startswith("postgres://") or database_url.startswith("postgresql://"):
        parsed = urlparse(database_url)
        return True, f"PostgreSQL at {parsed.hostname}:{parsed.port}"
    
    return False, f"Invalid DATABASE_URL format: {database_url[:30]}..."


def check_redis_url():
    """Check REDIS_URL format."""
    from urllib.parse import urlparse
    
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        # Try loading from .env
        try:
            from decouple import config
            redis_url = config("REDIS_URL", default="")
        except Exception:
            pass
    
    if not redis_url:
        return False, "REDIS_URL not configured (will use in-memory fallback in DEBUG mode)"
    
    # Check format
    if redis_url.startswith("redis://") or redis_url.startswith("rediss://"):
        parsed = urlparse(redis_url)
        scheme = "TLS" if redis_url.startswith("rediss://") else "TCP"
        return True, f"Redis {scheme} at {parsed.hostname}:{parsed.port}"
    
    return False, f"Invalid REDIS_URL format: {redis_url[:30]}..."


def check_django_dependencies():
    """Check if required Python packages are installed."""
    required = [
        ("django", "Django"),
        ("rest_framework", "Django REST Framework"),
        ("channels", "Django Channels"),
        ("redis", "Redis Python client"),
        ("decouple", "Python Decouple"),
    ]
    
    missing = []
    found = []
    
    for module, name in required:
        try:
            __import__(module)
            found.append(name)
        except ImportError:
            missing.append(name)
    
    if not missing:
        return True, f"All dependencies installed: {', '.join(found)}"
    return False, f"Missing packages: {', '.join(missing)}"


def main():
    """Run all checks and report results."""
    print("=" * 60)
    print("Wateen Environment Doctor")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Working Directory: {os.getcwd()}")
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("GDAL Library", check_gdal),
        ("Environment File", check_env_file),
        ("Database URL", check_database_url),
        ("Redis URL", check_redis_url),
        ("Django Dependencies", check_django_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"[Checking {name}]")
        try:
            ok, message = check_func()
            status = "[OK]" if ok else "[FAIL]"
            print(f"  {status} {message}")
            results.append((name, ok))
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for name, ok in results:
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {name}")
    
    print()
    
    # Recommendations
    failed = [name for name, ok in results if not ok]
    if failed:
        print("Recommendations:")
        if "GDAL Library" in failed:
            print()
            print("  [GDAL Installation Options]")
            print("  1. Install OSGeo4W from https://trac.osgeo.org/osgeo4w/")
            print("     - Select 'Express Install' -> 'GDAL'")
            print("     - Add to PATH: C:\\OSGeo4W\\bin")
            print()
            print("  2. Or run in Docker:")
            print("     cd docker && docker-compose up --build")
            print()
            print("  3. Or set GDAL_LIBRARY_PATH environment variable:")
            print("     set GDAL_LIBRARY_PATH=C:\\OSGeo4W\\bin\\gdal304.dll")
        
        if "Redis URL" in failed:
            print()
            print("  [Redis Configuration]")
            print("  - Redis is optional in DEBUG mode (uses in-memory fallback)")
            print("  - For production, set REDIS_URL in .env file")
            print("  - Example: REDIS_URL=redis://localhost:6379/0")
        
        if "Database URL" in failed:
            print()
            print("  [Database Configuration]")
            print("  - Set DATABASE_URL in .env file")
            print("  - Example: DATABASE_URL=postgres://user:pass@host:5432/db")
        
        return 1
    else:
        print("[OK] All checks passed! Environment is ready.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
