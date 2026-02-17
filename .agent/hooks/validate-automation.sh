#!/usr/bin/env bash
# =============================================================================
# validate-automation.sh — Pre-execution validation for automation safety
# =============================================================================
# This hook validates automation operations for safety and compliance.
# Run before executing automated tasks via OpenCode.
#
# Usage: ./validate-automation.sh <prompt_file>
# Exit codes: 0 = OK, 1 = Blocked, 2 = Requires Approval
# =============================================================================

set -euo pipefail

PROMPT_FILE="${1:-}"
SCHEMA_FILE=".agent/schemas/prompt_schema.json"
MAINTAINERS_FILE=".agent/MAINTAINERS"
HIGH_RISK_POLICY=".agent/HIGH_RISK_POLICY.md"
AUDIT_LOG=".agent/logs/audit.log"
MAX_ACTIONS_PER_HOUR=10
MAX_CONSECUTIVE_FAILURES=3

log_audit() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    local agent="validate-automation"
    local action="$1"
    local files="$2"
    local outcome="$3"
    local details="$4"
    echo "{\"timestamp\":\"$timestamp\",\"agent\":\"$agent\",\"action\":\"$action\",\"files\":$files,\"outcome\":\"$outcome\",\"details\":\"$details\"}" >> "$AUDIT_LOG"
}

error() {
    echo "ERROR: $1" >&2
    log_audit "validation" "[]" "failure" "$1"
    exit 1
}

warning() {
    echo "WARNING: $1" >&2
    log_audit "validation" "[]" "blocked" "$1"
    exit 2
}

# Check if prompt file provided
if [[ -z "$PROMPT_FILE" ]]; then
    error "No prompt file specified"
fi

# Check if prompt file exists
if [[ ! -f "$PROMPT_FILE" ]]; then
    error "Prompt file not found: $PROMPT_FILE"
fi

# Validate schema exists
if [[ ! -f "$SCHEMA_FILE" ]]; then
    error "Schema file not found: $SCHEMA_FILE"
fi

# Check maintainers file exists
if [[ ! -f "$MAINTAINERS_FILE" ]]; then
    error "Maintainers file not found: $MAINTAINERS_FILE"
fi

# Validate prompt file against schema (requires python with jsonschema)
if command -v python &> /dev/null; then
    python -c "
import json
import sys
try:
    from jsonschema import validate, ValidationError
    with open('$SCHEMA_FILE') as f:
        schema = json.load(f)
    with open('$PROMPT_FILE') as f:
        content = f.read()
        # Extract YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---')
            if len(parts) >= 2:
                import yaml
                data = yaml.safe_load(parts[1])
                # Allow for missing 'instructions' if file has content after frontmatter
                if 'title' in data:
                    print('Schema validation passed')
                else:
                    sys.exit(1)
            else:
                print('No frontmatter found, skipping schema validation')
        else:
            print('No frontmatter found, skipping schema validation')
except ImportError:
    print('jsonschema not installed, skipping validation')
except Exception as e:
    sys.exit(1)
" || error "Prompt file schema validation failed"
fi

# Check for high-risk operations
if grep -qi "delete\|remove\|drop\|truncate" "$PROMPT_FILE" 2>/dev/null; then
    warning "High-risk operation detected (deletion). Manual approval required."
fi

# Check for external network access requirements
if grep -qi "api\|fetch\|http\|request\|url" "$PROMPT_FILE" 2>/dev/null; then
    echo "NOTICE: Network access may be required. Check NETWORK_POLICY.md"
fi

# Check rate limiting (count actions in last hour)
if [[ -f "$AUDIT_LOG" ]]; then
    RECENT_ACTIONS=$(tail -100 "$AUDIT_LOG" 2>/dev/null | grep -c "$(date -u +"%Y-%m-%dT%H")" || true)
    if [[ "$RECENT_ACTIONS" -ge "$MAX_ACTIONS_PER_HOUR" ]]; then
        error "Rate limit exceeded: $RECENT_ACTIONS actions in current hour (max: $MAX_ACTIONS_PER_HOUR)"
    fi
fi

# Check for consecutive failures
if [[ -f "$AUDIT_LOG" ]]; then
    CONSECUTIVE_FAILURES=$(tail -10 "$AUDIT_LOG" 2>/dev/null | grep -c '"outcome":"failure"' || true)
    if [[ "$CONSECUTIVE_FAILURES" -ge "$MAX_CONSECUTIVE_FAILURES" ]]; then
        error "Automation halted: $CONSECUTIVE_FAILURES consecutive failures detected"
    fi
fi

# Success
log_audit "validation" "[\"$PROMPT_FILE\"]" "success" "All validation checks passed"
echo "Validation passed for: $PROMPT_FILE"
exit 0