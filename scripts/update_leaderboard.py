import os
from github import Github
from collections import defaultdict

def get_contributions():
    """Fetch contributions from GitHub API."""
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

    contributors = defaultdict(lambda: {'prs': 0, 'issues': 0, 'badges': []})

    # Get merged PRs (limit to recent ones for performance)
    prs = repo.get_pulls(state='closed')
    for pr in prs[:50]:  # Limit to avoid rate limits
        if pr.merged:
            user = pr.user.login
            contributors[user]['prs'] += 1

            # Check for specific file changes
            try:
                files = pr.get_files()
                file_names = [f.filename for f in files]

                if any('promptfooconfig.yaml' in name or 'eval.py' in name for name in file_names):
                    if '🥈 Practitioner' not in contributors[user]['badges']:
                        contributors[user]['badges'].append('🥈 Practitioner')

                if any('docs/03-design/adr/' in name or 'docs/07-operations/' in name for name in file_names):
                    if '🥇 Sage' not in contributors[user]['badges']:
                        contributors[user]['badges'].append('🥇 Sage')

                if '🥉 Initiate' not in contributors[user]['badges']:
                    contributors[user]['badges'].append('🥉 Initiate')
            except:
                # Skip if can't access files
                pass

    # Get issues (limit to recent ones)
    issues = repo.get_issues(state='all')
    for issue in issues[:50]:  # Limit to avoid rate limits
        if not issue.pull_request:
            user = issue.user.login
            contributors[user]['issues'] += 1

    return contributors

def generate_leaderboard(contributors):
    """Generate markdown leaderboard."""
    sorted_contributors = sorted(
        contributors.items(),
        key=lambda x: len(x[1]['badges']),
        reverse=True
    )

    leaderboard = "# Playbook Mastery Leaderboard\n\n"
    leaderboard += "**Last Updated:** 2026-04-18  \n"
    leaderboard += "**Owner:** Community Team\n\n"
    leaderboard += "## Overview\n\n"
    leaderboard += "This leaderboard recognizes contributors who have mastered different aspects of the AI Development Playbook. Badges are awarded based on contributions and engagement.\n\n"
    leaderboard += "## Current Leaderboard\n\n"
    leaderboard += "| Rank | GitHub Handle | Badges Earned | Contributions |\n"
    leaderboard += "|------|---------------|---------------|---------------|\n"

    for i, (user, data) in enumerate(sorted_contributors[:10], 1):  # Top 10
        badges = ' '.join(data['badges'])
        contributions = f"{data['prs']} PRs, {data['issues']} Issues"
        leaderboard += f"| {i}    | @{user} | {badges} | {contributions} |\n"

    leaderboard += "\n*This leaderboard updates daily via GitHub Action.*\n\n"
    leaderboard += "## How It Works\n\n"
    leaderboard += "- Badges are calculated based on merged PRs, opened issues, and repository stars.\n"
    leaderboard += "- Updates happen automatically every 24 hours.\n"
    leaderboard += "- See `BADGES.md` for badge criteria and `docs/00-onboarding/gamification.md` for details.\n"

    return leaderboard

def main():
    contributors = get_contributions()
    leaderboard = generate_leaderboard(contributors)

    with open('LEADERBOARD.md', 'w') as f:
        f.write(leaderboard)

if __name__ == "__main__":
    main()