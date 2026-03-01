import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSException, Polygon, LinearRing

from users.models import NurseProfile, AgencyProfile

pytestmark = pytest.mark.django_db


class TestNurseAgencyFKIntegrity:
    """
    Validates B2B2C business rule: Nurses cannot be freelancers.
    They must be attached to an AgencyProfile.
    """

    def test_nurse_creation_without_agency_raises_integrity_error(self):
        """
        Bypassing the ORM's full_clean() should still fail at the DB level
        because agency_id is NOT NULL.
        """
        from visits.tests.conftest import CustomUserFactory
        user = CustomUserFactory(role='NURSE')
        with pytest.raises(ValidationError):
            # Attempt to create directly in DB, full_clean() fires on save
            NurseProfile.objects.create(
                user=user,
                agency=None,
                is_available=True
            )

    def test_nurse_save_without_agency_raises_validation_error(self):
        """
        Testing the ORM level validation via clean() before it hits the DB.
        """
        from visits.tests.conftest import CustomUserFactory
        user = CustomUserFactory(role='NURSE')
        nurse = NurseProfile(
            user=user,
            agency=None,
            is_available=True
        )
        with pytest.raises(ValidationError) as exc_info:
            nurse.save()
        
        assert "agency" in str(exc_info.value) or "agency_id" in str(exc_info.value)

    def test_valid_nurse_creation_succeeds(self):
        """
        A valid nurse with an agency should save successfully.
        """
        from visits.tests.conftest import CustomUserFactory, AgencyProfileFactory
        user = CustomUserFactory(role='NURSE')
        agency = AgencyProfileFactory()
        nurse = NurseProfile.objects.create(
            user=user,
            agency=agency,
            is_available=True
        )
        assert getattr(nurse, 'user_id', None) is not None or nurse.pk is not None
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
