#!/usr/bin/env python3
"""
Project Scanner - Combines project code into a single file for AI analysis.
Overwrites existing output, includes timestamp and Git information.
"""

import os
import platform
from pathlib import Path
import subprocess  # For Git commands
from datetime import datetime

# ===== CONFIGURATION =====
FILE_TYPES = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css',
    '.md', '.txt', '.json', '.yml', '.yaml', '.xml', '.csv',
    '.java', '.c', '.cpp', '.h', '.sql', '.sh', '.bat', '.ps1'
}
SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', 'env',
    '.venv', 'dist', 'build', '.idea', '.vscode', 'target',
    'bin', 'obj', 'debug', 'release'
}
SKIP_FILES = {
    'package-lock.json', 'yarn.lock', '.ds_store', 'thumbs.db'
}
MAX_FILE_SIZE = 95 * 1024 * 1024 # 95 MB
# =========================

def is_windows():
    return platform.system().lower() == 'windows'

def should_skip_path(path):
    """Check if a file or directory should be skipped"""
    path_str = str(path).lower()

    # Check if any part matches skip directories
    for part in path.parts:
        if part.lower() in SKIP_DIRS:
            return True

    # Check if filename should be skipped
    if path.name.lower() in SKIP_FILES:
        return True

    return False

def get_git_info():
    """Retrieve Git branch, commit ID, and unstaged file count."""
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current']).decode('utf-8').strip()
        commit_id = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        status = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8')
        unstaged_files = len([line for line in status.splitlines() if line.startswith(' M') or line.startswith('??')])  # Modified or Untracked
        return branch, commit_id, unstaged_files
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None, 0

def scan_project(directory="."):
    """Scan project and combine code into a single string"""
    root_path = Path(directory).resolve()
    combined_code = ""
    file_count = 0

    # Get Git information
    branch, commit_id, unstaged_files = get_git_info()

    # Create timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add Git info to context
    context_header = f"""# 🚀 PROJECT CODE CONTEXT - {timestamp}\n\n"""
    context_header += f"Directory: {root_path}\n"

    if branch and commit_id:
        context_header += f"Git Branch: {branch}\n"
        context_header += f"Git Commit ID: {commit_id}\n"
        if unstaged_files > 0:
            context_header += f"🚨 Unstaged Changes: {unstaged_files} files\n"
    else:
        context_header += "⚠️ Not a Git repository\n"

    combined_code += context_header + "\n"

    print(f"🔍 Scanning: {root_path}")
    print(f"📁 File types: {', '.join(sorted(FILE_TYPES))}")
    print("─" * 50)

    for current_path in root_path.rglob("*"):
        if should_skip_path(current_path):
            continue

        if current_path.is_file():
            ext = current_path.suffix.lower()
            if ext in FILE_TYPES:
                try:
                    rel_path = current_path.relative_to(root_path)
                except ValueError:
                    rel_path = Path(str(current_path).replace(str(root_path), '').lstrip('\\/'))

                try:
                    with open(current_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        combined_code += f"\n\n# File: {rel_path}\n"
                        combined_code += code + "\n\n"
                        file_count += 1
                        print(f"📄 Processed: {rel_path}")
                except Exception as e:
                    combined_code += f"\n\n[Error reading {rel_path}: {e}]"

    combined_code += f"\n\n📊 Total files processed: {file_count}\n"

    return combined_code

def main():
    directory = input("Enter the project directory (or leave blank for current dir): ") or "."
    combined_code = scan_project(directory)

    output_file = "project_context.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined_code)
        print(f"✅ Code combined and saved to: {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()
