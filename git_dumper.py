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

def dump(cmd, out):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write("STDOUT:\n" + res.stdout)
        f.write("\nSTDERR:\n" + res.stderr)
        f.write("\nCODE: " + str(res.returncode))

dump("git branch", "git_branch_log.txt")
dump("git status", "git_status_log.txt")
dump("git diff HEAD", "git_diff_log.txt")
dump("git diff HEAD -- " + " ".join(files), "git_specific_diff_log.txt")
