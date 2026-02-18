
import os
import sys
import redis
import importlib.util

# Setup Path
sys.path.append(os.getcwd())

# Manually load .env file
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, value = line.strip().split('=', 1)
                    os.environ.setdefault(key, value)
                except ValueError:
                    continue

# Import settings directly without django.setup()
spec = importlib.util.spec_from_file_location("config.settings", os.path.join(os.getcwd(), "config", "settings.py"))
settings = importlib.util.module_from_spec(spec)
sys.modules["config.settings"] = settings
spec.loader.exec_module(settings)

def check_redis_cache():
    print("[-] Checking Redis Cache Connectivity...")
    try:
        # settings.CACHES['default']
        default_cache = settings.CACHES.get('default', {})
        options = default_cache.get('OPTIONS', {})
        location = default_cache.get('LOCATION')
        
        if not location:
            print("[FAIL] CACHES['default']['LOCATION'] not found.")
            return

        print(f"    Target: {location}")
        r = redis.from_url(location)
        r.set('audit_test_key', 'audit_test_value', ex=30)
        value = r.get('audit_test_key')
        
        if value == b'audit_test_value':
            print("[PASS] Redis Cache: Write/Read successful.")
        else:
            print(f"[FAIL] Redis Cache: Read mismatch. Got {value}")
            sys.exit(1)
            
    except Exception as e:
        print(f"[FAIL] Redis Cache Connection Error: {e}")
        sys.exit(1)

def check_redis_channels():
    print("[-] Checking Redis Channel Layer Connectivity...")
    try:
        channel_layers = getattr(settings, 'CHANNEL_LAYERS', {})
        default_layer = channel_layers.get('default', {})
        config = default_layer.get('CONFIG', {})
        hosts = config.get('hosts', [])
        
        if not hosts:
            print("[WARN] No hosts configured for Channel Layer.")
            return

        redis_url = hosts[0]
        print(f"    Target: {redis_url}")
        r = redis.from_url(redis_url)
        r.ping()
        print(f"[PASS] Redis Channel Layer: Connection verified.")
        
    except Exception as e:
        print(f"[FAIL] Redis Channel Layer Connection Error: {e}")
        # Not fatal if cache works, but good to know

def test_graceful_degradation_config():
    print("[-] Verifying Graceful Degradation Configuration...")
    try:
        default_cache = settings.CACHES.get('default', {})
        options = default_cache.get('OPTIONS', {})
        ignore_exceptions = options.get('IGNORE_EXCEPTIONS', False)
        
        if ignore_exceptions:
            print("[PASS] IGNORE_EXCEPTIONS is True. Graceful degradation enabled.")
        else:
            print("[FAIL] IGNORE_EXCEPTIONS is False or missing.")
            
    except Exception as e:
        print(f"[FAIL] Error checking config: {e}")

if __name__ == "__main__":
    print(f"Starting Redis Audit (Bypassing GDAL)...")
    check_redis_cache()
    check_redis_channels()
    test_graceful_degradation_config()
    print("\nAudit Complete.")
