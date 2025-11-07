#!/usr/bin/env python3

import os
import sys
import subprocess
from datetime import datetime

# Configuration
REPO_PATH = r"D:\Github\Gen-AI-Projects" # Change to your local repository path
BRANCH = "main"  # Change to your branch name

# Color codes for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.NC}")

def print_info(message):
    print(f"{Colors.YELLOW}→ {message}{Colors.NC}")

def run_command(command, error_message):
    """Execute a shell command and handle errors"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_PATH
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"{error_message}")
        print(f"Error details: {e.stderr}")
        sys.exit(1)

def check_for_changes():
    """Check if there are any changes to commit"""
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True,
        cwd=REPO_PATH
    )
    return bool(result.stdout.strip())

def main():
    # Verify repository path exists
    if not os.path.exists(REPO_PATH):
        print_error(f"Repository path does not exist: {REPO_PATH}")
        sys.exit(1)
    
    # Check if it's a git repository
    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        print_error(f"Not a git repository: {REPO_PATH}")
        sys.exit(1)
    
    print_info("Starting auto-push process...")
    
    # Check for changes
    if not check_for_changes():
        print_info("No changes to commit")
        sys.exit(0)
    
    # Generate commit message with timestamp
    commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Add all changes
    print_info("Adding files...")
    run_command("git add .", "Failed to add files")
    print_success("Files added")
    
    # Commit changes
    print_info("Committing changes...")
    run_command(f'git commit -m "{commit_message}"', "Failed to commit changes")
    print_success("Changes committed")
    
    # Push to GitHub
    print_info("Pushing to GitHub...")
    run_command(f"git push origin {BRANCH}", "Failed to push to GitHub")
    print_success("Successfully pushed to GitHub!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)