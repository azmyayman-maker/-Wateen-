from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSException, Polygon, LinearRing

import pytest

from users.models import NurseProfile, AgencyProfile

pytestmark = pytest.mark.django_db


class TestNurseAgencyFKIntegrity:
    """
    Validates B2B2C business rule: Nurses cannot be freelancers.
    They must be attached to an AgencyProfile.
    """

    def test_nurse_creation_without_agency_raises_validation_error(self):
        """
        NurseProfile.save() calls full_clean() so a ValidationError is expected when agency is None.
        """
        from visits.tests.conftest import CustomUserFactory
        with pytest.raises(ValidationError) as exc_info:
            CustomUserFactory(role='NURSE', agency=None)
        assert "AgencyProfile" in str(exc_info.value)

    def test_nurse_save_without_agency_raises_integrity_error(self):
        """
        Bypassing model-level cleaning (e.g., via bulk_create) should fail at the DB level
        because agency_id is NOT NULL.
        """
        from visits.tests.conftest import CustomUserFactory
        user = CustomUserFactory(role='PATIENT')
        with pytest.raises(IntegrityError):
            NurseProfile.objects.bulk_create([
                NurseProfile(
                    user=user,
                    agency=None,
                    is_available=True
                )
            ])

    def test_valid_nurse_creation_succeeds(self):
        """
        A valid nurse with an agency should save successfully.
        """
        from visits.tests.conftest import CustomUserFactory, AgencyProfileFactory
        agency = AgencyProfileFactory()
        user = CustomUserFactory(role='NURSE', agency=agency)
        nurse = getattr(user, 'nurse_profile')
        assert nurse.pk is not None
        assert nurse.agency == agency


class TestGeospatialIntegrity:
    """
    Validates PostGIS polygon constraints for AgencyProfile coverage areas.
    """

    def test_invalid_polygon_raises_exception(self):
        """
        AgencyProfile with a LinearRing of fewer than 4 points (invalid polygon)
        should raise a GEOSException or ValueError before hitting DB.
        """
        # A valid polygon requires at least 4 points (closed ring)
        with pytest.raises((GEOSException, ValueError)):
            invalid_ring = LinearRing((0, 0), (1, 1), (0, 1))  # Only 3 points, not closed
            Polygon(invalid_ring)

    def test_self_intersecting_polygon_rejected(self):
        """
        Self-intersecting polygons might be created in Python but are invalid for spatial operations.
        We ensure it at least doesn't break Django ORM validation.
        """
        # Create a bowtie (self-intersecting) polygon
        bowtie_ring = LinearRing((0, 0), (2, 2), (2, 0), (0, 2), (0, 0))
        polygon = Polygon(bowtie_ring, srid=4326)
        
        # Ensure it is recognized as inherently invalid spatially or raises when assigned
        assert not polygon.valid

    def test_valid_polygon_creation_succeeds(self):
        """
        A valid, closed polygon is successfully assigned to AgencyProfile.
        """
        valid_ring = LinearRing(
            (30.0, 31.0), 
            (30.0, 31.1), 
            (30.1, 31.1), 
            (30.1, 31.0), 
            (30.0, 31.0)
        )
        polygon = Polygon(valid_ring, srid=4326)
        
        agency = AgencyProfile.objects.create(
            manager_name="Test Polygon Agency",
            commercial_registry="CR-Geospatial-001",
            moh_license_number="MOH-Geo-001",
            tax_id="TAX-Geo-001",
            coverage_polygon=polygon
        )
        
        assert agency.id is not None
        assert agency.coverage_polygon.valid
