"""Diagnostic: run tests and write failures to a file."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_backend_comprehensive.py",
     "-v", "--tb=short", "-q"],
    capture_output=True, text=True, cwd="/app"
)

with open("/app/tests/diag_output.txt", "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(empty)")
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr or "(empty)")
    f.write(f"\n=== RETURN CODE: {result.returncode} ===\n")

print(f"Done. Return code: {result.returncode}")
