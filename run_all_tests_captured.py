import subprocess
import os
import sys

def run_tests():
    log_file = "all_tests_output.txt"
    # Ensure file exists
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("--- Starting Test Run ---\n")
    
    cmd = ["docker", "compose", "run", "--rm", "web", "python", "-m", "pytest", "-v", "--tb=short"]
    try:
        with open(log_file, "a", encoding="utf-8") as out:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            for line in process.stdout:
                out.write(line)
                out.flush()
                # Print to terminal for visibility if possible
                sys.stdout.write(line)
                sys.stdout.flush()
            process.wait()
            out.write(f"\n=== EXIT CODE: {process.returncode} ===\n")
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as out:
            out.write(f"CRITICAL ERROR: {e}\n")

if __name__ == "__main__":
    run_tests()
