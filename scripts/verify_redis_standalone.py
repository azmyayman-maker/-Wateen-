import os
import redis
import sys

# Load env vars if managing manually or assume they are set in run_command
redis_url = os.environ.get("REDIS_URL")

if not redis_url:
    print("REDIS_URL not set in environment.")
    sys.exit(1)

print(f"Testing connection to: {redis_url.split('@')[-1] if '@' in redis_url else '***'}")

try:
    r = redis.from_url(redis_url, socket_connect_timeout=5)
    r.ping()
    print("Redis Ping: SUCCESS")
    
    # Test Write/Read
    r.set("audit_test_key", "audit_test_value", ex=10)
    val = r.get("audit_test_key")
    if val == b"audit_test_value":
        print("Redis Read/Write: SUCCESS")
    else:
        print(f"Redis Read/Write: FAILED (Got {val})")
        
except Exception as e:
    print(f"Redis Connection FAILED: {e}")
    sys.exit(1)
