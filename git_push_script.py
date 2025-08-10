#!/usr/bin/env python3
"""
Git Push Script
This script will handle git operations to push all changes
"""

import subprocess
import sys
import os

def run_git_command(command, description):
    """Run a git command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    """Main function to handle git operations"""
    print("🚀 Git Push Script for Admission System Fixes")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run this from the project root.")
        return
    
    # Get current status
    print("\n📊 Current Git Status:")
    run_git_command("git status", "Checking git status")
    
    # Add all changes
    print("\n📁 Adding all changes...")
    if not run_git_command("git add .", "Adding all files"):
        print("❌ Failed to add files. Stopping.")
        return
    
    # Check what's staged
    print("\n📋 Staged changes:")
    run_git_command("git status --porcelain", "Checking staged files")
    
    # Commit changes
    print("\n💾 Committing changes...")
    commit_message = """Fix admission system: Replace hardcoded database paths with DATABASE variable

- Fixed all sqlite3.connect('users.db') instances in app.py and auth_handler.py
- Corrected AUTOINCREMENT typo in init_admission_access_table()
- Created comprehensive diagnostic script for admission system
- Updated status report tracking progress
- All database connections now use consistent DATABASE variable"""
    
    if not run_git_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("❌ Failed to commit. Stopping.")
        return
    
    # Push to remote
    print("\n🚀 Pushing to remote repository...")
    if not run_git_command("git push origin main", "Pushing to origin/main"):
        print("❌ Failed to push. Trying alternative branches...")
        
        # Try to find the current branch
        branch_result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True, timeout=10)
        if branch_result.returncode == 0:
            current_branch = branch_result.stdout.strip()
            print(f"🔄 Trying to push to current branch: {current_branch}")
            if not run_git_command(f"git push origin {current_branch}", f"Pushing to origin/{current_branch}"):
                print("❌ Failed to push to current branch as well.")
                return
        else:
            print("❌ Could not determine current branch.")
            return
    
    print("\n🎉 Git operations completed successfully!")
    print("\n📊 Final status:")
    run_git_command("git status", "Final status check")

if __name__ == "__main__":
    main()