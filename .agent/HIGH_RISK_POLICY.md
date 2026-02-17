# High-Risk Operations Policy

This document defines high-risk operations requiring manual approval,
as referenced in `.agent/workflows/ai_swarm.md` Section 6.6.

## High-Risk Operations Classification

### Critical (Always Requires Approval)

| Operation | Rationale | Approval Authority |
|-----------|-----------|-------------------|
| File deletions | Irreversible data loss | Lead Maintainer |
| Database migrations | Schema changes affect production | Lead Maintainer |
| External API calls | Data exfiltration risk | Any Maintainer |
| Credential changes | Security impact | Lead Maintainer |
| Authorization changes | Privilege escalation risk | Lead Maintainer |
| Network policy changes | Security perimeter | Lead Maintainer |
| Automation tag changes | Scope creep risk | Any Maintainer |

### Elevated (Approval for Non-Trivial Cases)

| Operation | Rationale | Approval Trigger |
|-----------|-----------|------------------|
| Batch file writes (>10 files) | Large surface area | >10 files modified |
| Dependency updates | Supply chain risk | Major version bumps |
| Configuration changes | Runtime behavior | Production configs |
| Test file modifications | Coverage gaps | Removing tests |

### Standard (Automated Execution OK)

| Operation | Conditions |
|-----------|------------|
| Single file write | Within project scope |
| Code formatting | No logic changes |
| Documentation updates | No code changes |
| Test additions | Adding coverage |

## Manual Approval Process

1. **Detection**: Hook script identifies high-risk operation
2. **Block**: Automation pauses before execution
3. **Notify**: Maintainer alerted via audit log + configured channel
4. **Approve**: Maintainer provides explicit approval
5. **Execute**: Operation proceeds with approval logged
6. **Record**: Full audit trail in `.agent/logs/audit.log`

## Rate Limiting Configuration

| Metric | Limit | Backoff |
|--------|-------|---------|
| Actions per hour | 10 | Exponential (2^n seconds) |
| Consecutive failures | 3 | Halt automation |
| File modifications per action | 50 | Warning, >100 blocked |

## Enforcement

This policy is enforced by:
- Pre-execution hook: `.agent/hooks/validate-automation.sh`
- CI/CD gate: Validation runs on all PRs affecting automation