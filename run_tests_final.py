import subprocess
import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
cmd = [sys.executable, "-m", "pytest", "users/coverage_tests.py", "-v", "--tb=short", "--no-header", "-x"]
try:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".", timeout=120)
    with open("test_run_output.txt", "w", encoding="utf-8") as f:
        f.write("=== STDOUT ===\n")
        f.write(result.stdout)
        f.write("\n=== STDERR ===\n")
        f.write(result.stderr)
        f.write(f"\n=== EXIT CODE: {result.returncode} ===\n")
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
except subprocess.TimeoutExpired:
    with open("test_run_output.txt", "w") as f:
        f.write("TEST RUN TIMED OUT AFTER 120 SECONDS\n")
    print("TEST RUN TIMED OUT AFTER 120 SECONDS")
except Exception as e:
    with open("test_run_output.txt", "w") as f:
        f.write(f"ERROR: {e}\n")
    print(f"ERROR: {e}")
