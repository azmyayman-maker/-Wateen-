import time

import pytest
from django.contrib.gis.geos import Point, Polygon

from users.models import AgencyProfile, AgencyStatus
from visits.services.geo_service import find_agencies_covering_point


# Helper function to generate a complex polygon (simulated)
def create_complex_poly(center_x, center_y, points=100):
    # Simplistic radial polygon for testing overhead
    from math import cos, pi, sin
    coords = []
    for i in range(points):
        angle = (i / points) * 2 * pi
        r = 0.5 + 0.1 * sin(5 * angle)
        coords.append((center_x + r * cos(angle), center_y + r * sin(angle)))
    coords.append(coords[0])
    return Polygon(coords)

@pytest.mark.django_db
class TestSpatialPerformance:
    def test_spatial_query_stress_mock(self):
        # Create 100 complex polygons
        for i in range(100):
            AgencyProfile.objects.create(
                manager_name=f"Stress Agency {i}",
                commercial_registry=f"reg-{i}",
                moh_license_number=f"moh-{i}",
                tax_id=f"tax-{i}",
                status=AgencyStatus.VERIFIED,
                coverage_polygon=create_complex_poly(31.0 + (i*0.01), 30.0)
            )

        start_time = time.time()
        point = Point(31.05, 30.05, srid=4326)

        # Execute multiple queries
        for _ in range(10):
            find_agencies_covering_point(point)

        duration = time.time() - start_time
        # Basic sanity check: 10 queries over 100 complex polys shouldn't take more than 5 seconds on a decent system (prevents CI flakiness)
        assert duration < 5.0

    def test_spatial_boundary_case(self):
        # Point exactly on the boundary of a square
        poly = Polygon.from_bbox((0, 0, 1, 1))
        AgencyProfile.objects.create(
            manager_name="Boundary Agency",
            commercial_registry="B1",
            moh_license_number="B2",
            tax_id="B3",
            status=AgencyStatus.VERIFIED,
            coverage_polygon=poly
        )

        point_on_edge = Point(0.5, 0, srid=4326)
        results = find_agencies_covering_point(point_on_edge)
        assert len(results) == 1
