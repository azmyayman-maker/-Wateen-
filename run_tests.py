import shutil
import subprocess
import sys

docker = shutil.which('docker')
if docker is None:
    print("ERROR: 'docker' not found on PATH", file=sys.stderr)
    sys.exit(127)

r = subprocess.run(
    [docker, 'compose', 'run', '--rm',
     '-e', 'AWS_STORAGE_BUCKET_NAME=dummy',
     '-e', 'DEBUG=True',
     'web', 'sh', '-c',
     'pip install -q -r requirements/dev.txt && python -m pytest visits/tests/test_geo_service.py visits/tests/test_spatial_performance.py visits/tests/test_geo_diagnostics.py -v --tb=short'],
    capture_output=True, text=True,
)

# Print only relevant lines from both stdout and stderr
for line in (r.stdout + r.stderr).splitlines():
    if any(kw in line for kw in ['PASSED', 'FAILED', 'ERROR', 'E ', '====', '----', 'assert']):
        print(line)
sys.exit(r.returncode)
