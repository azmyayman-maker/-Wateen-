import os

diff_file = 'all_diff.txt'
out_file = 'review_diffs.txt'

targets = [
    "agency_serializers.py",
    "coverage_tests.py",
    "coverage_views.py",
    "geo_service.py",
    "tasks.py",
    "Ticket-P3-T2-Final-Report.md",
    "run_pytest.py"
]

current_file = None
capture = False
collected = []

if os.path.exists(diff_file):
    with open(diff_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith('diff --git '):
                # check if it matches target
                capture = any(t in line for t in targets)
                if capture:
                    collected.append(line)
            elif capture:
                collected.append(line)

    with open(out_file, 'w', encoding='utf-8') as f:
        f.writelines(collected)
else:
    with open(out_file, 'w') as f:
        f.write("all_diff.txt not found")
