import subprocess
import os

with open("git_context.txt", "w", encoding="utf-8") as f:
    try:
        branch = subprocess.check_output("git branch", shell=True, text=True)
        f.write("=== BRANCH ===\n" + branch + "\n")
    except Exception as e:
        f.write("=== BRANCH ERROR ===\n" + str(e) + "\n")

    try:
        status = subprocess.check_output("git status", shell=True, text=True)
        f.write("=== STATUS ===\n" + status + "\n")
    except Exception as e:
        f.write("=== STATUS ERROR ===\n" + str(e) + "\n")
        
    try:
        diff_head = subprocess.check_output("git diff HEAD", shell=True, text=True)
        f.write("=== DIFF HEAD ===\n" + diff_head[:500] + "...\n")
    except Exception as e:
        f.write("=== DIFF HEAD ERROR ===\n" + str(e) + "\n")
