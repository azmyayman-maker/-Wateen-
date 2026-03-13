import os
import django
import time
import random
from decimal import Decimal
from django.contrib.gis.geos import Point

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from visits.models import Visit, VisitStatus
from users.models import AgencyProfile, AgencyStatus

def benchmark_spatial_matching(iterations=500):
    print(f"--- Benchmarking ST_Intersects for {iterations} iterations ---")
    
    # Cairo coordinates approximately
    base_lat = 30.0444
    base_lon = 31.2357
    
    start_time = time.time()
    latencies = []
    
    for i in range(iterations):
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        p = Point(lon, lat, srid=4326)
        
        q_start = time.time()
        # The core ST_Intersects query from request_views.py
        count = AgencyProfile.objects.filter(
            status=AgencyStatus.VERIFIED,
            coverage_polygon__intersects=p
        ).count()
        q_end = time.time()
        
        latencies.append((q_end - q_start) * 1000) # ms
    
    end_time = time.time()
    total_duration = end_time - start_time
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(iterations * 0.95)]
    
    print(f"Total time: {total_duration:.2f}s")
    print(f"Average Latency: {avg_latency:.2f}ms")
    print(f"95th Percentile: {p95_latency:.2f}ms")
    print(f"Throughput: {iterations / total_duration:.2f} requests/sec")
    
    # Check Index Hit Rate (Simulated for this script, but normally from PG stats)
    # Since we use GIST, hit rate is usually high after warming.
    
    return {
        "avg": avg_latency,
        "p95": p95_latency,
        "total": total_duration
    }

if __name__ == "__main__":
    benchmark_spatial_matching()
