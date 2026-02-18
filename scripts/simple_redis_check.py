
import os
import redis
import sys
from urllib.parse import urlparse

def check_redis():
    # Load .env manually
    env_path = os.path.join(os.getcwd(), '.env')
    redis_url = None
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith('REDIS_URL='):
                    redis_url = line.strip().split('=', 1)[1]
                    break
    
    if not redis_url:
        print("[FAIL] REDIS_URL not found in .env")
        sys.exit(1)
    
    # Redact credentials from URL for safe printing
    parsed = urlparse(redis_url)
    if parsed.password:
        redacted_netloc = f"{parsed.username}:***@{parsed.hostname}"
        if parsed.port:
            redacted_netloc += f":{parsed.port}"
        redacted_url = parsed._replace(netloc=redacted_netloc).geturl()
    else:
        redacted_url = redis_url
        
    print(f"Testing connection to: {redacted_url}")
    
    try:
        r = redis.from_url(redis_url, socket_timeout=5)
        if r.ping():
            print("[PASS] Successfully connected to Redis!")
        else:
            print("[FAIL] Connected but ping failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_redis()
