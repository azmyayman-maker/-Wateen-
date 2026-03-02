import subprocess, sys

r = subprocess.run(
    ['docker', 'compose', 'run', '--rm',
     '-e', 'AWS_STORAGE_BUCKET_NAME=dummy',
     '-e', 'DEBUG=True',
     'web', 'sh', '-c',
     'pip install -q -r requirements/dev.txt && python -m pytest users/tests/test_kyc_queue.py -v --tb=short'],
    capture_output=True, text=True,
)

# Print only relevant lines (results + failures)
for line in r.stdout.splitlines():
    if any(kw in line for kw in ['PASSED', 'FAILED', 'ERROR', 'E ', '====', '----', 'assert']):
        print(line)
sys.exit(r.returncode)
