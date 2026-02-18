# Research: Post-Audit Codebase Cleanup & Fixes

**Branch**: `001-audit-cleanup` | **Date**: 2026-02-19

## Overview

This is a remediation task based on specific audit findings. Research focuses on best practices for the identified issues.

## Research Findings

### 1. Socket Resource Cleanup

**Decision**: Use context manager for socket connections

**Rationale**: 
- Python's `socket.socket` supports context manager protocol (`with` statement)
- Ensures `sock.close()` is called even if exceptions occur
- Recommended pattern in Python documentation and PEP 343

**Implementation**:
```python
# Before
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(timeout)
result = sock.connect_ex((host, port))
sock.close()

# After
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
```

### 2. Redis PubSub Cleanup

**Decision**: Use try/finally pattern for pubsub cleanup

**Rationale**:
- Redis pubsub connections must be explicitly closed to prevent resource leaks
- `unsubscribe()` prevents receiving further messages on subscribed channels
- `close()` releases the connection back to the pool
- Order matters: unsubscribe first, then close

**Implementation**:
```python
pubsub = r.pubsub()
try:
    pubsub.subscribe(channel)
    # ... operations ...
finally:
    pubsub.unsubscribe()
    pubsub.close()
```

### 3. URL Password Masking Edge Cases

**Decision**: Handle password-only URLs by reconstructing netloc

**Rationale**:
- URLs like `redis://:password@host` have password but no username
- `urlparse` correctly extracts `password` but `username` is None
- Must manually reconstruct netloc: `f"{username or ''}:*****@{hostname}..."`

**Implementation**:
```python
if parsed.password:
    username = parsed.username or ''
    port_part = f":{parsed.port}" if parsed.port else ""
    masked_netloc = f"{username}:*****@{parsed.hostname}{port_part}"
```

### 4. Flake8 ARG001 Rule

**Decision**: Add `# noqa: ARG001` comment to suppress unused argument warning

**Rationale**:
- `pytest_configure(config)` is a pytest hook with required signature
- The `config` parameter is required by the hook contract even if unused
- ARG001 is the flake8-unused-arguments rule code
- `noqa` comment is the standard way to suppress specific warnings

### 5. Environment Variables in Docker Compose

**Decision**: Use `${VAR:-default}` syntax for environment variable substitution

**Rationale**:
- Docker Compose supports environment variable substitution natively
- `${VAR}` uses the variable directly
- `${VAR:-default}` provides a fallback if not set
- Hardcoded secrets in version control is a security vulnerability

### 6. Port Binding Security

**Decision**: Bind to `127.0.0.1:port:port` instead of `port:port`

**Rationale**:
- `port:port` binds to all interfaces (0.0.0.0), exposing services externally
- `127.0.0.1:port:port` binds only to localhost, preventing external access
- Redis and PostgreSQL should not be directly accessible from outside the host
- Docker internal networking still works regardless of host binding

## Alternatives Considered

| Issue | Alternative | Rejected Because |
|-------|-------------|------------------|
| Socket cleanup | Manual close in except block | More error-prone, duplicate code |
| Pubsub cleanup | Context manager (not available) | redis-py pubsub doesn't support context manager |
| URL masking | Regex replacement | Less reliable, edge cases harder to handle |
| Flake8 warning | Rename parameter to `_config` | Changes pytest hook signature, non-standard |

## References

- [Python socket documentation](https://docs.python.org/3/library/socket.html)
- [redis-py PubSub documentation](https://redis-py.readthedocs.io/en/stable/connections.html#pubsub)
- [Docker Compose variable substitution](https://docs.docker.com/compose/compose-file/variable-substitution/)
- [flake8-unused-arguments](https://pypi.org/project/flake8-unused-arguments/)
