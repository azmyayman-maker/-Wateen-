#!/bin/bash
# =============================================================================
# Wateen Project - Docker Entrypoint Script
# Production-Grade Service Orchestration with Self-Healing Capabilities
# =============================================================================

# Exit immediately if any command fails (errexit)
set -o errexit
# Fail if any variable is not set (nounset)
set -o nounset
# Propagate errors through pipes
set -o pipefail

# =============================================================================
# Configuration Constants
# =============================================================================

# Maximum number of connection attempts before giving up
readonly MAX_RETRIES=30

# Initial wait time in seconds (doubles each retry for exponential backoff)
readonly INITIAL_WAIT=1

# Maximum wait time cap in seconds (prevents excessive delays)
readonly MAX_WAIT=16

# Default values (can be overridden by environment variables)
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"

# =============================================================================
# Utility Functions
# =============================================================================

# Calculate wait time with exponential backoff
# Implements capped exponential backoff to prevent "Thundering Herd" problem
# Arguments:
#   $1 - Current attempt number
# Returns:
#   Wait time in seconds (capped at MAX_WAIT)
calculate_backoff() {
    local attempt=$1
    local wait_time=$((INITIAL_WAIT * (2 ** (attempt - 1))))
    
    # Cap the wait time at MAX_WAIT
    if (( wait_time > MAX_WAIT )); then
        echo "$MAX_WAIT"
    else
        echo "$wait_time"
    fi
}

# Check if a TCP port is open on a given host
# Uses netcat (nc) for port connectivity testing
# Arguments:
#   $1 - Hostname or IP address
#   $2 - Port number
# Returns:
#   0 if port is open, non-zero otherwise
check_tcp_port() {
    local host=$1
    local port=$2
    
    # Use nc with timeout to check port availability
    # -z: Zero I/O mode (just scan for open ports)
    # -w: Timeout in seconds
    nc -z -w 2 "$host" "$port" 2>/dev/null
}

# =============================================================================
# Service Wait Functions
# =============================================================================

# Wait for a service to become available with exponential backoff
# Implements robust retry logic with configurable timeouts
# Arguments:
#   $1 - Service name (for logging)
#   $2 - Hostname
#   $3 - Port number
# Returns:
#   0 if service is available, exits with 1 if max retries exceeded
wait_for_service() {
    local service_name=$1
    local host=$2
    local port=$3
    local attempt=1
    local wait_time
    
    echo "[INFO] Waiting for ${service_name} at ${host}:${port}..."
    
    while (( attempt <= MAX_RETRIES )); do
        if check_tcp_port "$host" "$port"; then
            echo "[SUCCESS] ${service_name} is available after ${attempt} attempt(s)"
            return 0
        fi
        
        # Calculate exponential backoff wait time
        wait_time=$(calculate_backoff "$attempt")
        
        echo "[RETRY ${attempt}/${MAX_RETRIES}] ${service_name} is unavailable - waiting ${wait_time}s before retry..."
        sleep "$wait_time"
        
        (( attempt++ ))
    done
    
    # All retries exhausted
    echo "[ERROR] ${service_name} failed to become available after ${MAX_RETRIES} attempts" >&2
    echo "[ERROR] Please check if the ${service_name} service is running and healthy" >&2
    exit 1
}

# Wait for PostgreSQL to be ready at the application level
# Uses pg_isready for more accurate database health checking
# Arguments:
#   $1 - Hostname
#   $2 - Port
#   $3 - Database name
#   $4 - Database user
# Returns:
#   0 if database is ready, exits with 1 if max retries exceeded
wait_for_postgres() {
    local host=$1
    local port=$2
    local db_name=$3
    local db_user=$4
    local attempt=1
    local wait_time
    
    echo "[INFO] Checking PostgreSQL readiness at ${host}:${port}..."
    
    while (( attempt <= MAX_RETRIES )); do
        # Use pg_isready for application-level health check
        # This verifies the database accepts connections, not just that the port is open
        if pg_isready -h "$host" -p "$port" -U "$db_user" -d "$db_name" -t 5 2>/dev/null; then
            echo "[SUCCESS] PostgreSQL is accepting connections after ${attempt} attempt(s)"
            return 0
        fi
        
        # Calculate exponential backoff wait time
        wait_time=$(calculate_backoff "$attempt")
        
        echo "[RETRY ${attempt}/${MAX_RETRIES}] PostgreSQL is not ready - waiting ${wait_time}s before retry..."
        sleep "$wait_time"
        
        (( attempt++ ))
    done
    
    echo "[ERROR] PostgreSQL failed to become ready after ${MAX_RETRIES} attempts" >&2
    exit 1
}

# Wait for Redis to be ready
# Uses redis-cli ping for application-level health checking
# Arguments:
#   $1 - Hostname
#   $2 - Port
# Returns:
#   0 if Redis is ready, exits with 1 if max retries exceeded
wait_for_redis() {
    local host=$1
    local port=$2
    local attempt=1
    local wait_time
    
    echo "[INFO] Checking Redis readiness at ${host}:${port}..."
    
    while (( attempt <= MAX_RETRIES )); do
        # Use redis-cli ping for application-level health check
        # This verifies Redis is actually responding, not just that the port is open
        if redis-cli -h "$host" -p "$port" ping 2>/dev/null | grep -q "PONG"; then
            echo "[SUCCESS] Redis is responding after ${attempt} attempt(s)"
            return 0
        fi
        
        # Calculate exponential backoff wait time
        wait_time=$(calculate_backoff "$attempt")
        
        echo "[RETRY ${attempt}/${MAX_RETRIES}] Redis is not ready - waiting ${wait_time}s before retry..."
        sleep "$wait_time"
        
        (( attempt++ ))
    done
    
    echo "[ERROR] Redis failed to become ready after ${MAX_RETRIES} attempts" >&2
    exit 1
}

# =============================================================================
# Main Execution
# =============================================================================

echo "=============================================="
echo "Wateen Docker Container Starting..."
echo "=============================================="
echo "[INFO] Environment Configuration:"
echo "  - DB_HOST: ${DB_HOST}"
echo "  - DB_PORT: ${DB_PORT}"
echo "  - REDIS_HOST: ${REDIS_HOST}"
echo "  - REDIS_PORT: ${REDIS_PORT}"
echo "=============================================="

# Wait for PostgreSQL (primary database)
# First check TCP connectivity, then verify database readiness
wait_for_service "PostgreSQL (TCP)" "${DB_HOST}" "${DB_PORT}"

# If pg_isready is available, do application-level check
if command -v pg_isready &>/dev/null && [[ -n "${DB_NAME:-}" ]] && [[ -n "${DB_USER:-}" ]]; then
    wait_for_postgres "${DB_HOST}" "${DB_PORT}" "${DB_NAME}" "${DB_USER}"
fi

# Wait for Redis (cache/broker)
# First check TCP connectivity, then verify Redis responsiveness
wait_for_service "Redis (TCP)" "${REDIS_HOST}" "${REDIS_PORT}"

# If redis-cli is available, do application-level check
if command -v redis-cli &>/dev/null; then
    wait_for_redis "${REDIS_HOST}" "${REDIS_PORT}"
fi

echo "=============================================="
echo "[INFO] All dependencies are ready!"
echo "[INFO] Starting application..."
echo "=============================================="

# Execute the main command (passed as arguments)
# Using exec replaces the shell with the application process
# This ensures proper signal handling (SIGTERM, SIGINT, etc.)
exec "$@"
