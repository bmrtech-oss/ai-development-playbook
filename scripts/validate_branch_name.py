#!/usr/bin/env python3
"""
Validate Git branch name follows naming conventions.
Used as a pre-commit hook.

Allowed patterns:
- feature/<description>
- release/v<version>
- hotfix/<description>
- main (protected)

Examples:
✓ feature/add-auth
✓ feature/improve-slm-training
✓ release/v1.2.0
✓ hotfix/fix-login-error
✗ Feature/add-auth (capitalized)
✗ feature_add_auth (underscores)
✗ feature/add auth (spaces)
"""

import re
import subprocess
import sys

# Allowed branch prefixes and their patterns
BRANCH_PATTERNS = {
    'feature': r'^feature/[a-z0-9\-]+$',
    'release': r'^release/v\d+\.\d+\.\d+(-[a-z0-9\-]+)?$',
    'hotfix': r'^hotfix/[a-z0-9\-]+$',
    'main': r'^main$',
    'develop': r'^develop$',  # Allowed for backward compat
}

def get_current_branch():
    """Get the current Git branch name."""
    try:
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        return branch
    except subprocess.CalledProcessError:
        return None

def validate_branch_name(branch):
    """Validate branch name against patterns."""
    # Allow detached HEAD state
    if branch == 'HEAD':
        return True, "Detached HEAD state (allowed)"

    # Check against patterns
    for pattern_name, pattern in BRANCH_PATTERNS.items():
        if re.match(pattern, branch):
            return True, f"Branch matches '{pattern_name}' pattern"

    return False, f"Branch '{branch}' does not match allowed patterns"

def main():
    branch = get_current_branch()
    
    if not branch:
        print("Error: Could not determine current branch")
        sys.exit(1)

    is_valid, message = validate_branch_name(branch)
    
    if is_valid:
        print(f"✓ {message}")
        return 0
    else:
        print(f"✗ {message}")
        print("\nAllowed branch patterns:")
        for pattern_name, pattern in BRANCH_PATTERNS.items():
            print(f"  - {pattern_name}: {pattern}")
        print("\nExamples:")
        print("  ✓ feature/add-auth")
        print("  ✓ release/v1.2.0")
        print("  ✓ hotfix/fix-login-error")
        return 1

if __name__ == '__main__':
    sys.exit(main())
