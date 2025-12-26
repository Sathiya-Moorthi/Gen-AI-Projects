import os
import subprocess
import sys

def run_git_command(command, cwd):
    """Executes a git command in the specified directory."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ Executed: {' '.join(command)}")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {' '.join(command)}")
        print(e.stderr)
        return False

def setup_gitignore(local_path):
    """Ensures sensitive files are ignored before pushing."""
    print("\n🔒 Performing Security Check (.gitignore)...")
    gitignore_path = os.path.join(local_path, ".gitignore")
    
    # Critical files to ignore
    entries_to_ignore = [
        ".env", 
        "__pycache__/", 
        "*.pyc", 
        ".DS_Store",
        "venv/",
        ".vscode/",
        ".idea/"
    ]
    
    current_content = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            current_content = f.read()
            
    with open(gitignore_path, "a") as f:
        for entry in entries_to_ignore:
            if entry not in current_content:
                f.write(f"\n{entry}")
                print(f"   Added '{entry}' to .gitignore")
            else:
                print(f"   Verified '{entry}' is ignored")

def push_to_github(local_path, repo_url, commit_message="Automated update"):
    """Main function to handle the git push process."""
    
    # 1. Validate Path
    if not os.path.exists(local_path):
        print(f"❌ Error: Path '{local_path}' does not exist.")
        return

    print(f"\n🚀 Starting Git Automation for:\n   Local: {local_path}\n   Remote: {repo_url}")

    # 2. Security Check (BEFORE PUSHING)
    setup_gitignore(local_path)

    # 3. Initialize Git if needed
    if not os.path.exists(os.path.join(local_path, ".git")):
        print("\nChecking for git initialization...")
        if not run_git_command(["git", "init"], local_path): return

    # 4. Configure Remote
    print("\n🔗 Configuring Remote...")
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"], 
            cwd=local_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        if result.returncode != 0:
            # Remote doesn't exist, add it
            if not run_git_command(["git", "remote", "add", "origin", repo_url], local_path): return
        else:
            # Remote exists, check if it matches
            current_url = result.stdout.strip()
            if current_url != repo_url:
                print(f"   Updating remote from '{current_url}' to '{repo_url}'")
                if not run_git_command(["git", "remote", "set-url", "origin", repo_url], local_path): return
            else:
                print("   Remote 'origin' is correctly configured.")
    except Exception as e:
        print(f"Error checking remote: {e}")
        return

    # 5. Add Files
    print("\n📦 Staging Files...")
    if not run_git_command(["git", "add", "."], local_path): return

    # 6. Commit
    print("\n💾 Committing Changes...")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=local_path, stdout=subprocess.PIPE, text=True)
    if status.stdout.strip():
        if not run_git_command(["git", "commit", "-m", commit_message], local_path): return
    else:
        print("   No changes to commit (working tree clean).")

    # 7. Push
    print("\n⬆️ Pushing to GitHub...")
    # Ensure branch is main
    run_git_command(["git", "branch", "-M", "main"], local_path)
    
    if not run_git_command(["git", "push", "-u", "origin", "main"], local_path):
        print("\n⚠️ Push failed. This often happens if the remote has changes you don't have.")
        print("   Attempting to pull (rebase) and push again...")
        if run_git_command(["git", "pull", "origin", "main", "--rebase"], local_path):
            run_git_command(["git", "push", "-u", "origin", "main"], local_path)

if __name__ == "__main__":
    # Interactive mode if args not provided
    if len(sys.argv) < 3:
        print("\n--- Git Push Automation Script ---")
        l_path = input("Enter Local Directory Path: ").strip()
        r_url = input("Enter GitHub Repo URL: ").strip()
        
        # Remove quotes if user added them
        l_path = l_path.strip('"').strip("'")
        r_url = r_url.strip('"').strip("'")
        
        if l_path and r_url:
            push_to_github(l_path, r_url)
        else:
            print("❌ Error: Both path and URL are required.")
    else:
        push_to_github(sys.argv[1], sys.argv[2])
