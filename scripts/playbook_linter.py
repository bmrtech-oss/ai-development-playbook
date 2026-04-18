import os
import re
import yaml
import argparse
import json

def check_file_exists(repo_path, file_path):
    """Check if a file exists in the repository."""
    return os.path.exists(os.path.join(repo_path, file_path))

def check_content_pattern(repo_path, file_path, pattern):
    """Check if a file contains a specific regex pattern."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return False
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return bool(re.search(pattern, content))

def run_checks(repo_path, strict_mode=False):
    """Run all compliance checks."""
    checks = {
        'model_card_template': {
            'file': 'docs/08-governance/model_card_template.md',
            'exists': check_file_exists(repo_path, 'docs/08-governance/model_card_template.md'),
            'patterns': [
                ('Contains owner field', r'Owner:'),
                ('Contains version field', r'Version:'),
            ] if strict_mode else []
        },
        'promptfoo_config': {
            'file': 'promptfooconfig.yaml',
            'exists': check_file_exists(repo_path, 'promptfooconfig.yaml'),
            'patterns': [
                ('Uses mock provider', r'provider:\s*\n\s*name:\s*mock'),
            ]
        },
        'incident_response_drill': {
            'file': 'docs/07-operations/incident_response_runbook.md',
            'exists': check_file_exists(repo_path, 'docs/07-operations/incident_response_runbook.md'),
            'patterns': [
                ('Contains drill section', r'Incident Response Drills'),
            ]
        },
        'feature_flags_in_ci': {
            'file': '.gitlab-ci.yml',
            'exists': check_file_exists(repo_path, '.gitlab-ci.yml'),
            'patterns': [
                ('Uses feature flags', r'FEATURE_FLAG'),
            ]
        },
        'pgvector_drift_query': {
            'file': 'docs/07-operations/observability/rag_hygiene_dashboard.md',
            'exists': check_file_exists(repo_path, 'docs/07-operations/observability/rag_hygiene_dashboard.md'),
            'patterns': [
                ('Contains pgvector query', r'pgvector'),
            ]
        }
    }

    results = {}
    for check_name, check_data in checks.items():
        result = {'exists': check_data['exists'], 'issues': []}
        if not check_data['exists']:
            result['issues'].append(f"File {check_data['file']} not found")
        else:
            for pattern_name, pattern in check_data['patterns']:
                if not check_content_pattern(repo_path, check_data['file'], pattern):
                    result['issues'].append(f"{pattern_name} not found in {check_data['file']}")
        results[check_name] = result

    return results

def generate_markdown_report(results):
    """Generate a markdown report."""
    report = "# Playbook Compliance Report\n\n"
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if not r['issues'])

    report += f"**Summary:** {passed_checks}/{total_checks} checks passed\n\n"

    for check_name, result in results.items():
        status = "✅" if not result['issues'] else "❌"
        report += f"## {status} {check_name.replace('_', ' ').title()}\n\n"
        if result['issues']:
            report += "Issues:\n" + "\n".join(f"- {issue}" for issue in result['issues']) + "\n\n"
        else:
            report += "All checks passed.\n\n"

    return report

def generate_json_report(results):
    """Generate a JSON report."""
    return json.dumps(results, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Playbook Linter')
    parser.add_argument('--repo-path', required=True, help='Path to the repository to lint')
    parser.add_argument('--strict', action='store_true', help='Enable strict mode')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown', help='Output format')
    parser.add_argument('--fail-on-warning', action='store_true', help='Fail on warnings')

    args = parser.parse_args()

    results = run_checks(args.repo_path, args.strict)

    if args.format == 'markdown':
        report = generate_markdown_report(results)
        with open('lint-report.md', 'w') as f:
            f.write(report)
    else:
        report = generate_json_report(results)
        with open('lint-report.json', 'w') as f:
            f.write(report)

    # Check if we should fail
    has_issues = any(result['issues'] for result in results.values())
    if has_issues and args.fail_on_warning:
        exit(1)

if __name__ == "__main__":
    main()