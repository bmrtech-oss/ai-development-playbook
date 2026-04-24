# Branching Strategy Quick Examples

This guide provides quick reference examples for common branching workflows using our Git branching strategy.

## Quick Start Scenarios

### Scenario 1: Adding a New Feature

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/add-user-auth

# 2. Develop incrementally
# - Make commits regularly with descriptive messages
# - Use feature flags to hide incomplete functionality
git add .
git commit -m "feat: add user authentication endpoints with flag"

# 3. Push early and often
git push -u origin feature/add-user-auth

# 4. Create Pull Request (via GitHub UI)
# - Add description: what, why, how
# - Reference feature flags used
# - Link related issues

# 5. Once approved and CI passes, merge
git checkout main
git pull origin main
git merge --squash feature/add-user-auth
git push origin main

# 6. Delete feature branch
git push origin --delete feature/add-user-auth
```

### Scenario 2: Merging Unfinished Code with Feature Flags

```bash
# Feature is incomplete but safe with feature flags
git checkout -b feature/experimental-slm

# Wrap new code in feature flags
# In your config/featureFlags.ts or config.py:
# - Add: FEATURE_EXPERIMENTAL_SLM_ENABLED=false (default)

# Code:
if featureFlags.isEnabled('experimental-slm'):
    result = run_new_slm_model()
else:
    result = run_existing_model()

# Commit and merge to main (disabled by default)
git push origin feature/experimental-slm
# Create PR, get review, merge
git checkout main
git merge feature/experimental-slm
git push origin main

# In CI/staging, enable the flag for testing
# FEATURE_EXPERIMENTAL_SLM_ENABLED=true npm test
```

### Scenario 3: Creating a Release

```bash
# 1. Ensure all features ready and tested on main
git checkout main
git pull origin main

# 2. Create release branch
git checkout -b release/v1.2.0

# 3. Only bug fixes and docs on release branch
git commit -m "docs: update changelog for v1.2.0"
git commit -m "fix: patch critical bug in auth"

# 4. Merge fixes back to main
git checkout main
git pull origin main
git merge release/v1.2.0
git push origin main

# 5. Tag and deploy
git checkout main
git tag v1.2.0
git push origin main
git push origin v1.2.0

# 6. Delete release branch
git push origin --delete release/v1.2.0
```

### Scenario 4: Hotfix for Production

```bash
# 1. Branch from main (production)
git checkout main
git pull origin main
git checkout -b hotfix/fix-login-error

# 2. Fix the issue
# - Keep it focused and minimal
git add .
git commit -m "fix: resolve login timeout issue"
git push -u origin hotfix/fix-login-error

# 3. Create PR, get quick review
# - Mark as HIGH PRIORITY
# - Link to incident

# 4. Merge to main
git checkout main
git merge hotfix/fix-login-error
git push origin main

# 5. If release branch exists, cherry-pick
git checkout release/v1.2.0
git cherry-pick <commit-hash>
git push origin release/v1.2.0

# 6. Cleanup
git push origin --delete hotfix/fix-login-error
```

## Commit Message Convention

Follow Conventional Commits for clear, scannable history:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`  
**Scope:** `auth`, `api`, `ui`, `slm`, etc.

**Examples:**
```
feat(auth): add JWT token validation with feature flag
fix(slm): resolve model timeout during inference
docs(branching): update release workflow
```

## Common Branch Naming Patterns

| Use Case | Pattern | Example |
|----------|---------|---------|
| Auth feature | `feature/auth-*` | `feature/auth-jwt-tokens` |
| SLM feature | `feature/slm-*` | `feature/slm-inference-optimization` |
| UI feature | `feature/ui-*` | `feature/ui-dark-mode` |
| Bugfix | `hotfix/*` | `hotfix/session-timeout` |
| Release prep | `release/v*` | `release/v1.2.0` |

## Checking Branch Status

```bash
# List local branches
git branch

# List all branches (local + remote)
git branch -a

# See branch history (visual)
git log --graph --oneline --all

# Delete local branch (after merge)
git branch -d feature/add-auth

# Force delete unmerged branch
git branch -D feature/abandoned
```

## Useful Aliases

Add to `.git/config` or `~/.gitconfig`:

```
[alias]
    feat = "!f() { git checkout -b feature/$1; }; f"
    hotfix = "!f() { git checkout -b hotfix/$1; }; f"
    release = "!f() { git checkout -b release/v$1; }; f"
    sync = "!git fetch origin && git rebase origin/main"
```

**Usage:**
```bash
git feat add-auth          # Creates feature/add-auth
git hotfix fix-bug         # Creates hotfix/fix-bug
git release 1.2.0          # Creates release/v1.2.0
git sync                   # Fetches and rebases on main
```

## Troubleshooting

### Accidentally committed to main?
```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Stash changes, switch branches
git stash
git checkout -b feature/fix
git stash pop
```

### Need to rebase before merge?
```bash
git fetch origin
git rebase origin/main
git push -f origin feature/my-feature  # Force push only on feature branches!
```

### Multiple commits should be squashed?
```bash
# Interactive rebase (last 3 commits)
git rebase -i HEAD~3
# Mark commits as 's' (squash) or 'f' (fixup)
# Force push after squash
git push -f origin feature/my-feature
```

## References

- Full guide: [../branching-strategy.md](../branching-strategy.md)
- Commit standards: [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
- Feature flags implementation: [../branching-strategy.md#feature-flags-for-unfinished-code](../branching-strategy.md#feature-flags-for-unfinished-code)
- Setup guide: [git-hooks-ci-cd-setup.md](git-hooks-ci-cd-setup.md)
