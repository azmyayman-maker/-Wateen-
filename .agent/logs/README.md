# Execution Logs

This directory stores execution logs including:
- `audit.log` - Audit trail of all automated actions

## Audit Log Format

The audit log uses JSON Lines format (one JSON object per line) with the following schema:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "agent": "OpenCode",
  "action": "file_write",
  "files": ["src/module.py", "tests/test_module.py"],
  "outcome": "success",
  "details": "Created new authentication module"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 string | UTC timestamp of the action |
| `agent` | string | Agent that performed the action (e.g., "OpenCode", "Antigravity") |
| `action` | string | Type of action performed |
| `files` | array of strings | List of files affected (empty if none) |
| `outcome` | string | "success", "failure", or "blocked" |
| `details` | string | Human-readable description |

### Action Types

- `file_read` - File read operation
- `file_write` - File created or modified
- `file_delete` - File deleted
- `command_exec` - Shell command executed
- `api_call` - External API call made
- `automation_start` - Automated task started
- `automation_halt` - Automation stopped (error or manual intervention)

### Retention Policy

- Logs are retained for 90 days
- Rotation begins when log exceeds 10MB
- Archived logs: `.agent/logs/audit.log.1`, `.agent/logs/audit.log.2`, etc.

See `.agent/workflows/ai_swarm.md` Section 6.5 for logging requirements.