import subprocess
import os
import sys
from datetime import datetime

def run_git_command(command: list, cwd: str) -> bool:
    """Runs a Git command and prints its output. Returns True on success, False on error."""
    try:
        print(f"\nExecuting Git command: {' '.join(command)} in {cwd}")
        process = subprocess.run(
            command,
            cwd=cwd,
            check=True,  # Raise an exception for non-zero exit codes
            capture_output=True,
            text=True
        )
        print("STDOUT:")
        print(process.stdout)
        if process.stderr:
            print("STDERR:")
            print(process.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError executing Git command: {' '.join(command)}")
        print(f"Return Code: {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print("\nError: Git command not found. Please ensure Git is installed and in your system's PATH.")
        return False

def automate_git_for_ai_rails(project_path: str):
    """
    Automates Git operations for AI Rails integration:
    - Creates a backup branch and commits current state.
    - Creates a new working branch for AI Rails development.
    """
    project_repo_path = os.path.abspath(project_path)
    print(f"Starting Git automation for project: {project_repo_path}")

    if not os.path.isdir(os.path.join(project_repo_path, ".git")):
        print(f"Error: '{project_repo_path}' is not a Git repository. Please initialize it first.")
        return False

    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_branch_name = f"ai-rails-backup-{current_time}"
    working_branch_name = "ai-rails-dev" # Standard branch for AI Rails work

    # --- Step 1: Create a backup branch and commit current state ---
    print("\n--- Step 1: Creating a backup branch and committing current state ---")
    if not run_git_command(["git", "checkout", "-b", backup_branch_name], project_repo_path):
        print("Failed to create backup branch. Aborting Git automation.")
        return False
    
    if not run_git_command(["git", "add", "."], project_repo_path):
        print("Failed to add files for backup commit. Aborting Git automation.")
        return False

    backup_commit_message = f"AI Rails: Pre-integration backup - {current_time}"
    if not run_git_command(["git", "commit", "-m", backup_commit_message], project_repo_path):
        print("Failed to commit current state to backup branch. Aborting Git automation.")
        return False

    print(f"Successfully created backup branch '{backup_branch_name}' and committed current state.")

    # --- Step 2: Push the backup branch to remote (optional but recommended) ---
    print("\n--- Step 2: Pushing backup branch to remote (recommended) ---")
    print(f"ACTION REQUIRED: Please ensure you have push access and run:")
    print(f"  git push -u origin {backup_branch_name}")
    print("If you prefer not to push now, you can skip this step, but pushing is safer.")
    
    # We cannot automate the 'git push' without user credentials or SSH setup.
    # So, we'll prompt the user here. The script will continue, assuming they will push later.
    input("Press Enter to continue (after pushing backup branch manually if desired)...")


    # --- Step 3: Create and switch to the new working branch for AI Rails dev ---
    print(f"\n--- Step 3: Creating and switching to new working branch '{working_branch_name}' ---")
    if not run_git_command(["git", "checkout", "-b", working_branch_name], project_repo_path):
        print(f"Failed to create or checkout working branch '{working_branch_name}'. Aborting Git automation.")
        return False
    print(f"Successfully created and switched to working branch '{working_branch_name}'.")

    print("\n--- Git Automation Complete ---")
    print(f"You are now on branch '{working_branch_name}'.")
    print(f"Your previous state is backed up on branch '{backup_branch_name}'.")
    print("Remember to regularly commit and push your work on the working branch!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python git_automation.py <path_to_existing_project_repo>")
        sys.exit(1)

    project_path_arg = sys.argv[1]
    automate_git_for_ai_rails(project_path_arg)