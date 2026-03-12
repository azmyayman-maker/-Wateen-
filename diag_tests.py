import subprocess
import sys
import os

LOG_PATH = r"C:\Users\AdminOS\.gemini\antigravity\brain\c520f195-4693-4ecd-9a3e-1fef7eba3bb1\diag_report.txt"

def log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run(cmd):
    log(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        log(f"Exit Code: {result.returncode}")
        log("--- STDOUT ---")
        log(result.stdout)
        log("--- STDERR ---")
        log(result.stderr)
        log("-" * 20)
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    
    log("DIAGNOSTIC START")
    run(["docker", "--version"])
    run(["python", "--version"])
    run(["python", "manage.py", "--version"])
    run(["dir"])
    # Try a simple pytest on a single file if possible
    run(["docker", "compose", "run", "--rm", "web", "python", "-m", "pytest", "users/coverage_tests.py", "-v", "--tb=short", "-c", "pytest.ini"])
    log("DIAGNOSTIC END")
