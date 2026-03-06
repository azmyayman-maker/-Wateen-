import subprocess

def run_cmd(cmd, outfile):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        with open(outfile, "wb") as f:
            f.write(output)
    except subprocess.CalledProcessError as e:
        with open(outfile, "wb") as f:
            f.write(e.output)

run_cmd("git status", "git_status_out.txt")
run_cmd("git diff HEAD", "git_diff_head.txt")
run_cmd("git diff --cached", "git_diff_cached.txt")
run_cmd("git diff", "git_diff_unstaged.txt")
