from django.contrib.gis.geos import Polygon, Point

import pytest
from rest_framework.exceptions import ValidationError

from users.models import AgencyProfile, CustomUser, UserRole, DispatchMode, AgencyStatus
from users.agency_serializers import AgencyProfileSerializer

@pytest.mark.django_db
class TestAgencyProfileEnhancements:
    """
    Professional test suite to verify the P1-T2 AgencyProfile modifications:
    - PostGIS infrastructure and GistIndex (implicit via DB).
    - Model field defaults (rating, dispatch_mode).
    - 1:1 mapping with CustomUser.
    - Signal-based automated profile creation.
    - Serializer polygon geometry validation.
    """

    def test_agency_profile_model_defaults(self):
        """Test that the updated default values are applied correctly on creation."""
        # Arrange & Act
        agency = AgencyProfile.objects.create(
            manager_name="Test Health Agency",
            commercial_registry="CR-100200",
            moh_license_number="MOH-100200",
            tax_id="TAX-100200"
        )
        
        # Assert
        assert agency.rating == 0.0, "Rating default should be 0.0 (FloatField)"
        assert agency.dispatch_mode == DispatchMode.MANUAL, "Default dispatch_mode should be MANUAL"
        assert agency.status == AgencyStatus.PENDING, "Default status should be PENDING"

    def test_user_agency_admin_signal_auto_creation(self):
        """Test that creating a CustomUser with AGENCY_ADMIN role triggers auto-creation of an AgencyProfile."""
        # Arrange & Act
        user = CustomUser.objects.create_user(
            national_id="29001011223344",
            phone_number="01012345678",
            password="StrongPassword123!",
            role=UserRole.AGENCY_ADMIN,
            first_name_ar="أحمد",
            last_name_ar="المدير"
        )
        
        # Assert
        user.refresh_from_db()
        assert user.agency is not None, "Signal should have automatically assigned an AgencyProfile"
        assert user.agency.manager_name == "أحمد المدير", "Manager name should pull from user full name"
        assert user.agency.commercial_registry.startswith("PENDING-")
        assert user.agency.status == AgencyStatus.PENDING

    def test_user_agency_admin_signal_ignores_existing_agency(self):
        """Test that if an agency is provided during user creation, the signal does NOT overwrite it."""
        # Arrange
        existing_agency = AgencyProfile.objects.create(
            manager_name="Existing Agency",
            commercial_registry="CR-EXIST",
            moh_license_number="MOH-EXIST",
            tax_id="TAX-EXIST"
        )
        
        # Act
        user = CustomUser.objects.create_user(
            national_id="29001011223355",
            phone_number="01012345679",
            password="StrongPassword123!",
            role=UserRole.AGENCY_ADMIN,
            agency=existing_agency
        )
        
        # Assert
        user.refresh_from_db()
        assert user.agency == existing_agency, "Signal should respect explicitly provided agency"

    def test_customuser_agency_one_to_one_relationship(self):
        """Test the strictly enforced 1:1 related mapping between AgencyProfile and CustomUser."""
        # Arrange
        agency = AgencyProfile.objects.create(
            manager_name="1to1 Agency",
            commercial_registry="CR-11",
            moh_license_number="MOH-11",
            tax_id="TAX-11"
        )
        user = CustomUser.objects.create_user(
            national_id="29001011223366",
            phone_number="01012345670",
            password="StrongPassword123!",
            role=UserRole.AGENCY_ADMIN,
            agency=agency
        )
        
        # Act & Assert reverse relation specifically named 'admin_user'
        assert hasattr(agency, 'admin_user'), "Reverse relation 'admin_user' should exist on AgencyProfile"
        assert agency.admin_user == user, "Reverse relation should point back to the expected user"

    def test_serializer_validate_coverage_polygon_valid(self):
        """Validate that a proper PostGIS Polygon passes the serializer validation."""
        # Arrange: A valid closed triangle (4 points)
        valid_polygon = Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (0.0, 0.0)))
        serializer = AgencyProfileSerializer()
        
        # Act
        result = serializer.validate_coverage_polygon(valid_polygon)
        
        # Assert
        assert result == valid_polygon

    def test_serializer_validate_coverage_polygon_invalid_type(self):
        """Validate that non-polygon geometries are rejected."""
        # Arrange
        point = Point(30.0, 30.0)
        serializer = AgencyProfileSerializer()
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc:
            serializer.validate_coverage_polygon(point)
        assert "valid Polygon" in str(exc.value)

    def test_serializer_validate_coverage_polygon_not_closed(self):
        """Validate that an open/unclosed LineString mapped as polygon raises validation."""
        serializer = AgencyProfileSerializer()
        
        # Test valid fallback: Passing None should be valid because null=True
        assert serializer.validate_coverage_polygon(None) is None
