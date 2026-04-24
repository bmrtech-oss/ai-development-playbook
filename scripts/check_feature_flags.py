#!/usr/bin/env python3
"""
Check for orphaned or misconfigured feature flags in the codebase.
Used as a pre-commit hook to catch feature flag issues early.

Checks:
- Feature flags are defined before use
- No dead flags (defined but never used)
- Consistent naming patterns
- Proper cleanup markers for flags nearing end-of-life
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

# Patterns for feature flag definitions and usages
FLAG_DEFINITION_PATTERNS = [
    r'FEATURE_\w+_ENABLED',
    r'featureFlags\.isEnabled\(["\'](\w+)["\']\)',
    r'isFeatureEnabled\(["\'](\w+)["\']\)',
]

class FeatureFlagChecker:
    def __init__(self):
        self.defined_flags: Set[str] = set()
        self.used_flags: Set[str] = set()
        self.warnings: list = []
        self.errors: list = []

    def check_file(self, filepath: Path) -> bool:
        """Check a single file for feature flag issues."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to read {filepath}: {e}")
            return False

        # Extract definitions
        env_vars = re.findall(r'FEATURE_(\w+)_ENABLED', content)
        self.defined_flags.update(env_vars)

        # Extract usages
        usages = re.findall(r'isEnabled\(["\'](\w+)["\']\)', content)
        self.used_flags.update(usages)

        # Check for deprecation markers
        if 'DEPRECATED_FLAG' in content or 'TODO: remove flag' in content:
            deprecated = re.findall(r'(FEATURE_\w+).*(?:DEPRECATED|TODO.*remove)', content)
            if deprecated:
                self.warnings.append(f"{filepath}: Contains deprecated flags: {deprecated}")

        return True

    def analyze(self) -> Tuple[bool, list]:
        """Analyze collected flag data."""
        issues = []

        # Check for undefined flags (used but not defined)
        undefined = self.used_flags - self.defined_flags
        if undefined:
            for flag in undefined:
                issues.append(f"⚠ Used but not defined: {flag}")

        # Check for dead flags (defined but not used)
        dead = self.defined_flags - self.used_flags
        if dead:
            for flag in dead:
                issues.append(f"ℹ Defined but not used: {flag} (consider removing)")

        return len(undefined) == 0, issues

def main():
    if len(sys.argv) < 2:
        print("Usage: check_feature_flags.py <files...>")
        return 0  # Pre-commit hook: exit 0 if no files specified

    checker = FeatureFlagChecker()
    
    # Check all provided files
    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if filepath.exists():
            checker.check_file(filepath)

    # Analyze results
    is_valid, issues = checker.analyze()

    if issues:
        print("Feature Flag Analysis:")
        for issue in issues:
            print(f"  {issue}")

    if checker.errors:
        print("\nErrors encountered:")
        for error in checker.errors:
            print(f"  ✗ {error}")
        return 1

    if not is_valid:
        print("\n⚠ Some features flags are not properly defined. Please fix before committing.")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
