import logging

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import AgencyProfile, CustomUser, UserRole, KYCDocument, KYCDocumentType
from .validators import validate_kyc_file_extension_and_size

logger = logging.getLogger(__name__)

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
    
    # KYC Documents (Mandatory for registration)
    commercial_registry_file = serializers.FileField(
        write_only=True, required=True, validators=[validate_kyc_file_extension_and_size]
    )
    moh_license_file = serializers.FileField(
        write_only=True, required=True, validators=[validate_kyc_file_extension_and_size]
    )
    tax_id_file = serializers.FileField(
        write_only=True, required=True, validators=[validate_kyc_file_extension_and_size]
    )
    
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
            'admin_password',
            'commercial_registry_file',
            'moh_license_file',
            'tax_id_file',
        ]
        read_only_fields = ['id', 'status']

    @transaction.atomic
    def create(self, validated_data: dict) -> AgencyProfile:
        # Extract administrative and document data
        admin_national_id = validated_data.pop('admin_national_id')
        admin_phone_number = validated_data.pop('admin_phone_number')
        admin_password = validated_data.pop('admin_password')
        
        # Extract files
        cr_file = validated_data.pop('commercial_registry_file')
        moh_file = validated_data.pop('moh_license_file')
        tax_file = validated_data.pop('tax_id_file')
        
        # Track created KYC documents for file cleanup on failure
        created_docs: list[KYCDocument] = []
        try:
            # 1. Create the Agency Profile (defaults to PENDING status)
            agency = AgencyProfile.objects.create(**validated_data)
            
            # 2. Create the initial AgencyAdmin user linked to this agency
            CustomUser.objects.create_user(
                national_id=admin_national_id,
                phone_number=admin_phone_number,
                password=admin_password,
                role=UserRole.AGENCY_ADMIN,
                agency=agency,
            )

            # 3. Create the initial KYC Documents (v1 auto-assigned by model)
            for doc_type, doc_file in [
                (KYCDocumentType.COMMERCIAL_REGISTRY, cr_file),
                (KYCDocumentType.MOH_LICENSE, moh_file),
                (KYCDocumentType.TAX_ID, tax_file),
            ]:
                doc = KYCDocument.objects.create(
                    agency=agency,
                    document_type=doc_type,
                    file=doc_file,
                )
                created_docs.append(doc)
            
            # 4. Notify SuperAdmins (Async after transaction commit)
            from .services.notifications import AgencyNotificationService
            transaction.on_commit(
                lambda: AgencyNotificationService.notify_superadmins_of_new_registration(
                    agency_id=str(agency.id),
                    manager_name=agency.manager_name
                )
            )
            
            return agency
        except Exception:
            # DB rows will be rolled back by @transaction.atomic, but
            # files already written to storage are NOT part of the DB tx.
            for doc in created_docs:
                try:
                    doc.file.delete(save=False)
                except Exception as exc:
                    logger.error(
                        "Failed to clean up orphaned file for KYCDocument "
                        "(agency=%s, type=%s): %s",
                        getattr(doc, 'agency_id', '?'),
                        getattr(doc, 'document_type', '?'),
                        exc,
                    )
            raise


class AgencyApprovalSerializer(serializers.ModelSerializer):
    """
    Used by SuperAdmins to approve or reject an agency.
    """
    class Meta:
        model = AgencyProfile
        fields = ['status']


class KYCDocumentUpdateSerializer(serializers.ModelSerializer):
    """
    Handles re-upload of a specific KYC document (e.g., after rejection).
    The model.save() method handles version incrementing automatically.
    """
    file = serializers.FileField(
        required=True, 
        validators=[validate_kyc_file_extension_and_size]
    )

    class Meta:
        model = KYCDocument
        fields = ['document_type', 'file']

    def create(self, validated_data: dict) -> KYCDocument:
        # Agency is injected by the view (e.g. from the request context or URL)
        return KYCDocument.objects.create(**validated_data)


class KYCDocumentSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for KYC documents, providing secure pre-signed URLs.
    """
    presigned_url = serializers.SerializerMethodField()
    document_type_display = serializers.CharField(
        source='get_document_type_display', read_only=True
    )

    class Meta:
        model = KYCDocument
        fields = [
            'id', 
            'document_type', 
            'document_type_display',
            'status', 
            'version', 
            'uploaded_at', 
            'presigned_url',
            'reviewer_notes'
        ]
        read_only_fields = fields

    def get_presigned_url(self, obj) -> str | None:
        """
        Generate a short-lived secure link (Law 151/2020 protocol).
        """
        if not obj.file:
            return None
            
        from .services.storage import KYCStorageService
        return KYCStorageService.get_presigned_url(obj.file.name)
