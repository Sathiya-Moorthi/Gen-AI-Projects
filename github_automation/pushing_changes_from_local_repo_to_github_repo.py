import os
import subprocess
from datetime import datetime

# === CONFIGURATION ===
LOCAL_REPO_PATH = r"D:\Github\Gen-AI-Projects"  # your local repo path
BRANCH_NAME = "main"                        # or 'master'
COMMIT_MESSAGE = f"Auto-update on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# === FUNCTION ===
def run_git_command(command):
    """Run a git command in the repo folder."""
    result = subprocess.run(command, cwd=LOCAL_REPO_PATH, shell=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"❌ Error running: {command}\n{result.stderr}")
    else:

        print(f"✅ {command}\n{result.stdout.strip()}")

# === MAIN ===
print("🔄 Starting Git automation...")

# check status
run_git_command("git status")

# Stage all changes
run_git_command("git add .")

# Commit changes
run_git_command(f'git commit -m "{COMMIT_MESSAGE}"')

# Push to GitHub
run_git_command("git push origin " + BRANCH_NAME)

print("🎉 Files successfully pushed to GitHub!")
