import logging
import sys
import time

from visits.services.matching import GeoMatchingService

# Configure logging to stdout
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_smoke_test():
    print("\n--- STARTING SMOKE TEST ---")
    try:
        svc = GeoMatchingService()

        # 1. Add dummy nurse at Tahrir Square (30.0444, 31.2357)
        nurse_id = 999
        print(f"Adding nurse {nurse_id} at Tahrir Square...")
        success = svc.update_nurse_location(nurse_id, 30.0444, 31.2357)

        if not success:
            print("❌ FAILED: Could not update nurse location. Check Redis connection.")
            return False

        print("✅ Nurse added successfully.")

        # Give Redis a moment to propagate if needed (usually instant)
        time.sleep(0.1)

        # 2. Search nearby (Start search 100m away)
        # Lat: 30.0450, Lng: 31.2360
        print("Searching for candidates within 5km...")
        candidates = svc.find_candidates(30.0450, 31.2360, radius_km=5)

        found = any(c['nurse_id'] == nurse_id for c in candidates)

        if found:
            print(f"✅ SUCCESS: Redis is reachable and Geo-Engine found nurse {nurse_id}!")
            print(f"   Candidates: {candidates}")
        else:
            print("❌ FAILED: Nurse added but not found in search results.")
            print(f"   Candidates found: {candidates}")
            return False

        # 3. Clean up
        print("Cleaning up...")
        svc.remove_nurse(nurse_id)
        return True

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False
    finally:
        print("--- END SMOKE TEST ---\n")

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
