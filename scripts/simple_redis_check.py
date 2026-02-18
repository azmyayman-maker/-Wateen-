
import os
import redis
import sys

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
        
    print(f"Testing connection to: {redis_url}")
    
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
