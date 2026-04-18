# Tech Lead Release Checklist

**Role:** Rotating (monthly)  
**Goal:** Ensure a smooth, boring release.

## Week Before Release
- [ ] Review open bugs targeting the release milestone.
- [ ] Confirm all feature flags are documented.
- [ ] Ping owners of stale PRs.

## Release Day (Tuesday)
- [ ] Create release branch from `main`.
- [ ] Run full CI pipeline (including AI evaluation).
- [ ] Tag version `vX.Y.Z`.
- [ ] Deploy to staging and smoke test.
- [ ] Announce in #eng-announce that release is imminent.

## Post‑Release (Wednesday)
- [ ] Monitor dashboards for 24h.
- [ ] Close the release milestone in GitLab.
- [ ] Write a brief release summary (what shipped, any known issues).
