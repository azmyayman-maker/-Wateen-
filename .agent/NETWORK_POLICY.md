# Network Access Policy

This document defines the network whitelist process for automated operations
as referenced in `.agent/workflows/ai_swarm.md` Section 6.4.

## Network Whitelist Process

### Where Whitelist is Stored

Network access requirements are declared in task prompt files under the
`network_access` field (see `.agent/schemas/prompt_schema.json`).

Example:
```yaml
---
title: "Fetch External API Data"
network_access:
  - "api.example.com"
  - "cdn.example.com"
---
```

### Allowed Network Categories

| Category | Allowed Domains | Approval Required |
|----------|-----------------|-------------------|
| Package Managers | pypi.org, npmjs.org | No |
| Version Control | github.com, gitlab.com | No |
| External APIs | Declared per-task | Yes |
| Custom Services | Declared per-task | Yes |

### Approval Process

1. **Declaring Network Access**: Task prompts must list required external hosts
   in the `network_access` field.

2. **High-Risk Domains**: Any domain not in the allowed categories requires
   maintainer approval before automation can proceed.

3. **Deny by Default**: Network access is blocked unless explicitly whitelisted.

## Sandbox Enforcement

OpenCode runs in a restricted execution environment:
- **File System**: Scoped to project directory only
- **Network**: TCP/UDP traffic filtered by whitelist
- **Process**: No shell escape, no privileged operations

## External Whitelist Configuration

For Docker-based execution, network restrictions are enforced via:
- `.agent/config/network_whitelist.json` (runtime whitelist)
- Docker network policies (infrastructure layer)

## Violations

Unauthorized network access attempts are:
1. Logged to `.agent/logs/audit.log`
2. Reported to maintainers
3. Subject to automation halt per Section 6.6