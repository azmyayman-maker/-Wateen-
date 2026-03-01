from rest_framework import serializers
from .models import AgencyProfile, CustomUser, UserRole
from django.db import transaction
from django.contrib.auth.hashers import make_password

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
