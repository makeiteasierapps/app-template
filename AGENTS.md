# App Template AGENTS Guide

This template is the default starting point for platform apps. Keep it production-ready, simple to adopt, and aligned with platform deployment flows.

## Template Intent

- Provide a dependable baseline for new apps with minimal setup friction.
- Stay compatible with Observatory-driven deployment and GitOps promotion flow.
- Favor clear defaults over heavy framework complexity.

## Compatibility Guidance

When changing template behavior, verify alignment with:

- Observatory deployment assumptions (manifests, env var injection, health path expectations)
- GitOps image update workflow and repo conventions
- Platform auth/session model used for deployed apps

## Security Guidance

- Keep secure-by-default behavior for auth, cookies, and API access patterns.
- Avoid patterns that encourage hardcoded secrets.
- Document any new required secrets/environment variables clearly.

## Documentation Expectations

If developer workflow or deployment expectations change, update `README.md` and any relevant examples in the same change.

## Change Discipline

- Keep template changes broadly reusable across app types.
- Avoid coupling the template to a single app's domain logic.
- Prefer small, clear upgrades that reduce maintenance overhead for a solo operator.
