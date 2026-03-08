import os
import sys
import time
import math
import random
import django
from django.db import connection

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.gis.geos import Polygon, Point
from users.models import CustomUser, AgencyProfile, AgencyStatus
from visits.services.geo_service import find_agencies_covering_point

# Center of Cairo roughly
BASE_LAT = 30.0444
BASE_LNG = 31.2357

def generate_complex_polygon(center_lng, center_lat, num_vertices=120, radius=0.05):
    """
    Generates a complex pseudo-circle polygon with jagged edges.
    """
    points = []
    for i in range(num_vertices):
        angle = (i / num_vertices) * 2 * math.pi
        # Add some random jaggedness to radius
        r = radius * (1.0 + random.uniform(-0.1, 0.1))
        lng = center_lng + r * math.cos(angle)
        lat = center_lat + r * math.sin(angle)
        points.append((lng, lat))
    
    # Close the polygon
    points.append(points[0])
    poly = Polygon(points, srid=4326)
    return poly

def setup_benchmark_data(num_agencies=500):
    print(f"Setting up {num_agencies} complex agencies for benchmarking...")
    
    # Because we're in benchmarking, let's delete anything we made previously using raw SQL to bypass broken ORM cascades
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {CustomUser._meta.db_table} WHERE national_id LIKE '290010101%%'")
        cursor.execute(f"DELETE FROM {AgencyProfile._meta.db_table} WHERE manager_name LIKE 'BenchAgency_%%'")

    agencies_to_create = []
    users_to_create = []
    
    for i in range(num_agencies):
        # Create a unique center near Cairo
        c_lng = BASE_LNG + random.uniform(-0.5, 0.5)
        c_lat = BASE_LAT + random.uniform(-0.5, 0.5)
        
        poly = generate_complex_polygon(c_lng, c_lat, num_vertices=120, radius=0.03)
        
        nid = f"290010101{str(i).zfill(5)}"
        phone = f"01299{str(i).zfill(6)}"
        
        user = CustomUser(
            national_id=nid,
            phone_number=phone,
            role="AGENCY_ADMIN"
        )
        user.set_password("testpassword")
        users_to_create.append(user)
        
        agency = AgencyProfile(
            manager_name=f"BenchAgency_{i}",
            commercial_registry=f"CR-BENCH-{i}",
            moh_license_number=f"MOH-BENCH-{i}",
            tax_id=f"TAX-BENCH-{i}",
            status=AgencyStatus.VERIFIED,
            coverage_polygon=poly,
            rating=5.0
        )
        agencies_to_create.append(agency)

    # Bulk create agencies first to get their IDs
    created_agencies = AgencyProfile.objects.bulk_create(agencies_to_create)
    
    # Associate users with created agencies
    for i, user in enumerate(users_to_create):
        user.agency = created_agencies[i]
        
    # Now bulk create users
    CustomUser.objects.bulk_create(users_to_create)
    print(f"✅ {num_agencies} complex agencies and users created.")

def run_performance_test():
    # Point near Cairo that will intersect some of the generated polygons
    test_point = Point(BASE_LNG, BASE_LAT, srid=4326)
    
    print("\n--- Running Query Performance Benchmark ---")
    
    # Warm up query
    list(find_agencies_covering_point(test_point))
    
    iterations = 20
    total_time = 0.0
    
    for _ in range(iterations):
        start = time.perf_counter()
        # Force evaluation
        agencies = list(find_agencies_covering_point(test_point))
        end = time.perf_counter()
        total_time += (end - start)
        
    avg_time_ms = (total_time / iterations) * 1000
    print(f"Average query execution time over {iterations} iterations: {avg_time_ms:.2f} ms")
    
    if avg_time_ms > 50.0:
        print("❌ FAILED: Query execution time exceeds 50ms.")
    else:
        print("✅ PASSED: Query execution time is under 50ms.")
        
    print("\n--- EXPLAIN ANALYZE Output ---")
    
    # Get the raw SQL and explain analyze it
    qs = find_agencies_covering_point(test_point)
    raw_query = str(qs.query)
    
    # We execute explain analyze directly
    explain_sql = f"EXPLAIN ANALYZE {raw_query}"
    
    with connection.cursor() as cursor:
        try:
            # Need to pass params explicitly to execute
            sql, params = qs.query.sql_with_params()
            cursor.execute(f"EXPLAIN ANALYZE {sql}", params)
            plan = cursor.fetchall()
            for row in plan:
                print(row[0])
                
            # Verify if GIST index is used
            plan_str = " ".join([row[0] for row in plan])
            if "Index Scan" in plan_str and "users_agency_profile_coverage_polygon" in plan_str.lower():
                print("\n✅ Verification PASSED: Query used the GIST index.")
            elif "Index Scan" in plan_str or "Bitmap Index Scan" in plan_str:
                print("\n✅ Verification PASSED: Query used an index.")
            else:
                print("\n⚠️ WARNING: Query might be executing a Sequential Scan!")
        except Exception as e:
            print(f"Error running EXPLAIN ANALYZE: {e}")

if __name__ == "__main__":
    try:
        setup_benchmark_data(500)
        run_performance_test()
    finally:
        print("\nCleaning up...")
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {CustomUser._meta.db_table} WHERE national_id LIKE '290010101%%'")
            cursor.execute(f"DELETE FROM {AgencyProfile._meta.db_table} WHERE manager_name LIKE 'BenchAgency_%%'")
