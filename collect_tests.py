import subprocess, sys, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
cmd = [sys.executable, "-m", "pytest", "users/coverage_tests.py", "--collect-only", "-q"]
try:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print("STDOUT:", r.stdout)
    print("STDERR:", r.stderr[-500:] if len(r.stderr) > 500 else r.stderr)
    print("EXIT:", r.returncode)
except subprocess.TimeoutExpired:
    print("TIMED OUT after 30s")
except Exception as e:
    print(f"ERROR: {e}")
