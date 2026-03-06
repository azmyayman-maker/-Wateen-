import subprocess

files = [
    "users/agency_serializers.py",
    "users/coverage_tests.py",
    "users/coverage_views.py",
    "visits/services/geo_service.py",
    "visits/tasks.py",
    "docs/reports/Ticket-P3-T2-Final-Report.md",
    "run_pytest.py"
]

try:
    # Get staged and unstaged diff for these files
    output = subprocess.check_output(["git", "diff", "HEAD", "--"] + files, stderr=subprocess.STDOUT)
    with open("specific_diff.txt", "wb") as f:
        f.write(output)
except subprocess.CalledProcessError as e:
    with open("specific_diff.txt", "wb") as f:
        f.write(e.output)
