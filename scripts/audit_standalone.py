import os
import sys
import psycopg2
import redis
from decouple import config

# Add project root to path for relative config loading if needed,
# but we use decouple which finds .env in parent dirs.


def check_postgres():
    print("\n--- Checking PostgreSQL (Neon) ---")
    db_url = config("DATABASE_URL", default=None)
    if not db_url:
        print("[FAIL] DATABASE_URL not found in .env")
        return False

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT postgis_version();")
        version = cur.fetchone()[0]
        print(f"[OK] Connected to PostgreSQL. PostGIS Version: {version}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL Connection Error: {e}")
        return False


def check_redis():
    print("\n--- Checking Redis (Cloud) ---")
    redis_url = config("REDIS_URL", default=None)
    if not redis_url:
        print("[FAIL] REDIS_URL not found in .env")
        return False

    try:
        r = redis.from_url(redis_url)
        r.ping()
        print("[OK] Redis Connected (Ping success)")

        # Geo Test
        key = "audit:geo_test_standalone"
        r.delete(key)

        # redis-py expects a flat list: [lon, lat, member, lon, lat, member, ...]
        # Using the correct syntax for redis-py 5.x+
        try:
            count = r.geoadd(key, [31.2357, 30.0444, "Cairo_Tower"])
        except (redis.exceptions.ResponseError, TypeError):
            # Fallback for older redis-py versions: geoadd(name, lon, lat, member)
            try:
                count = r.geoadd(key, 31.2357, 30.0444, "Cairo_Tower")
            except Exception as fallback_error:
                print(f"[FAIL] Redis Geo add failed: {fallback_error}")
                return False

        proxs = r.georadius(key, 31.2357, 30.0444, 1, unit="km")

        # Decode if bytes
        proxs = [p.decode() if isinstance(p, bytes) else p for p in proxs]

        if "Cairo_Tower" in proxs:
            print("[OK] Redis Geo module active")
        else:
            print(f"[FAIL] Redis Geo test returned: {proxs}")
            r.delete(key)
            return False

        r.delete(key)
        return True

    except Exception as e:
        print(f"[FAIL] Redis Error: {e}")
        return False


if __name__ == "__main__":
    print("Starting Standalone Infrastructure Audit...")
    pg_ok = check_postgres()
    redis_ok = check_redis()

    if pg_ok and redis_ok:
        print("\n[SUCCESS] Infrastructure Audit Passed.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Infrastructure Audit Failed.")
        sys.exit(1)
