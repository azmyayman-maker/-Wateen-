from django.contrib.auth.hashers import make_password
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import AgencyProfile, CustomUser, UserRole

class AgencyProfileSerializer(GeoFeatureModelSerializer):
    """
    Serializer for AgencyProfile with GeoFeatureModel serialization.
    """
    class Meta:
        model = AgencyProfile
        geo_field = 'coverage_polygon'
        fields = [
            'id',
            'manager_name',
            'commercial_registry',
            'moh_license_number',
            'tax_id',
            'coverage_polygon',
            'status',
            'rating',
            'dispatch_mode',
            'wallet_balance',
        ]
        read_only_fields = ['id', 'status', 'rating', 'wallet_balance']

    def validate_coverage_polygon(self, value: Polygon | MultiPolygon | None) -> Polygon | MultiPolygon | None:
        """
        Enforce spatial requirements for the coverage_polygon geometry.
        """
        if value is None:
            return value

        # Only accept Polygon or MultiPolygon
        if not isinstance(value, (Polygon, MultiPolygon)):
            raise serializers.ValidationError(_("The geometry must be a valid Polygon."))

        # Extract the polygon (handle MultiPolygon by taking the first one for validation purposes)
        # Assuming the requirement is just one unified closed area
        polygons = [value] if isinstance(value, Polygon) else value

        for poly in polygons:
            # GEOS instances validate automatically in Django, but we enforce the specific ring requirements
            if poly.empty:
                raise serializers.ValidationError(_("The polygon cannot be empty."))

            # 2. The polygon is closed (linear ring)
            # 3. The polygon has at least 3 distinct vertices (4 coordinates including the closing point)
            exterior_ring = poly.exterior_ring
            if not exterior_ring.is_closed:
                raise serializers.ValidationError(_("The polygon must be closed (linear ring)."))

            if len(exterior_ring.coords) < 4:
                raise serializers.ValidationError(_("The polygon must have at least 3 distinct vertices."))

        return value

class AgencyRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles the registration of a new B2B Agency and its initial AgencyAdmin user.
    Expects nested data for the admin user.
    """
    admin_national_id = serializers.CharField(write_only=True, required=True, max_length=14)
    admin_phone_number = serializers.CharField(write_only=True, required=True, max_length=15)
    admin_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = AgencyProfile
        fields = [
            'id',
            'manager_name',
            'commercial_registry',
            'moh_license_number',
            'tax_id',
            'status',
            'admin_national_id',
            'admin_phone_number',
            'admin_password'
        ]
        read_only_fields = ['id', 'status']

    @transaction.atomic
    def create(self, validated_data):
        admin_national_id = validated_data.pop('admin_national_id')
        admin_phone_number = validated_data.pop('admin_phone_number')
        admin_password = validated_data.pop('admin_password')
        
        # 1. Create the Agency Profile (defaults to PENDING status)
        agency = AgencyProfile.objects.create(**validated_data)
        
        # 2. Create the initial AgencyAdmin user linked to this agency
        CustomUser.objects.create(
            national_id=admin_national_id,
            phone_number=admin_phone_number,
            password=make_password(admin_password),
            role=UserRole.AGENCY_ADMIN,
            agency=agency,  # Link the admin to the agency for RBAC
        )
        
        return agency


class AgencyApprovalSerializer(serializers.ModelSerializer):
    """
    Used by SuperAdmins to approve or reject an agency.
    """
    class Meta:
        model = AgencyProfile
        fields = ['status']
