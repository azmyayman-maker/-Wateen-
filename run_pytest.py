import subprocess

try:
    cmd = "poetry run pytest -q users/test_coverage_poly.py::TestAgencyCoverageValidation::test_valid_polygon_upload"
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    with open("tests_out.txt", "wb") as f:
        f.write(output)
except subprocess.CalledProcessError as e:
    with open("tests_out.txt", "wb") as f:
        f.write(e.output)
