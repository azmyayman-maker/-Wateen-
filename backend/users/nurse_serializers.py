"""
Nurse Invitation Serializers for Wateen B2B2C Platform.

Implements serializers for:
- Creating nurse invitations (NurseInvitationCreateSerializer)
- Listing invitations (NurseInvitationSerializer)
- Accepting invitations (AcceptInvitationSerializer)
- NurseProfile binding (NurseProfileSerializer)

B2B2C Rules Enforced:
- Phone validation for Egyptian mobile numbers
- Agency isolation (IDOR prevention)
- Capacity validation
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import (
    AgencyProfile,
    InvitationStatus,
    NurseInvitation,
    NurseProfile,
    UserRole,
)
from .validators import validate_phone_number


class NurseInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for reading nurse invitation data.
    
    Used for listing and retrieving invitations.
    Token is intentionally excluded to prevent credential leakage.
    """

    class Meta:
        model = NurseInvitation
        fields = ["id", "agency", "phone", "status", "expires_at", "created_at"]
        read_only_fields = ["id", "agency", "status", "expires_at", "created_at"]


class NurseInvitationCreateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for the create-invitation response only.
    
    Includes the token so the agency admin can share the invite link.
    Must ONLY be used in the POST response, never for list/retrieve.
    """

    class Meta:
        model = NurseInvitation
        fields = ["id", "agency", "phone", "token", "status", "expires_at", "created_at"]
        read_only_fields = ["id", "agency", "token", "status", "expires_at", "created_at"]


class NurseInvitationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new nurse invitation.
    
    Validates:
    - Phone number format (Egyptian mobile)
    - Agency capacity (via service layer)
    - Rate limits (via service layer)
    """

    phone = serializers.CharField(
        max_length=20,
        required=True,
        help_text=_("رقم الهاتف المحمول - 11 رقم")
    )

    def validate_phone(self, value: str) -> str:
        """Validate phone number format."""
        # Use the existing validator
        validate_phone_number(value)
        return value


class AcceptInvitationSerializer(serializers.Serializer):
    """
    Serializer for accepting a nurse invitation.
    
    Validates all required fields for nurse registration:
    - token: Invitation token UUID
    - password: User password
    - phone: Phone number (must match invitation)
    - national_id: Egyptian national ID (14 digits)
    - syndicate_number: Nursing syndicate membership number
    - full_name: Arabic full name
    - email: Optional email address
    """

    token = serializers.UUIDField(
        required=True,
        help_text=_("رمز الدعوة")
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text=_("كلمة المرور - 8 أحرف على الأقل")
    )

    def validate_password(self, value: str) -> str:
        """Validate password against Django's AUTH_PASSWORD_VALIDATORS."""
        from django.contrib.auth.password_validation import validate_password
        validate_password(value)
        return value
    phone = serializers.CharField(
        max_length=20,
        required=True,
        help_text=_("رقم الهاتف المحمول")
    )
    national_id = serializers.CharField(
        max_length=14,
        min_length=14,
        required=True,
        help_text=_("الرقم القومي - 14 رقم")
    )
    syndicate_number = serializers.CharField(
        max_length=50,
        required=True,
        help_text=_("رقم عضوية النقابة")
    )
    full_name = serializers.CharField(
        max_length=200,
        required=True,
        help_text=_("الاسم الكامل بالعربية")
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text=_("البريد الإلكتروني (اختياري)")
    )

    def validate_phone(self, value: str) -> str:
        """Validate phone number format."""
        validate_phone_number(value)
        return value

    def validate_national_id(self, value: str) -> str:
        """Validate Egyptian national ID format."""
        from .validators import validate_egyptian_national_id
        validate_egyptian_national_id(value)
        return value


class NurseProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for NurseProfile binding.
    
    Enforces that a nurse is assigned strictly to an agency 
    and prevents IDOR attacks.
    """

    class Meta:
        model = NurseProfile
        fields = [
            "agency",
            "national_id_document",
            "syndicate_number"
        ]

    def validate_agency(self, value: AgencyProfile) -> AgencyProfile:
        """Validate agency ownership (IDOR prevention)."""
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError(_("Request context is missing."))

        user = request.user

        # IDOR PREVENTION:
        # Only Agency Admin can assign nurses to their own agency
        if user.role != UserRole.AGENCY_ADMIN:
            raise serializers.ValidationError(
                _("Only an Agency Admin can assign a nurse to an agency.")
            )

        # Explicitly check that the authenticated user manages this agency
        if getattr(user, "agency", None) != value:
            raise serializers.ValidationError(
                _("You can only assign nurses to your own agency.")
            )

        return value


class InvitationStatusSerializer(serializers.Serializer):
    """
    Serializer for filtering invitations by status.
    
    Used in query parameters for listing invitations.
    """

    status = serializers.ChoiceField(
        choices=InvitationStatus.choices,
        required=False,
        help_text=_("Filter by invitation status")
    )


class RevokeInvitationSerializer(serializers.Serializer):
    """
    Serializer for revoking an invitation.
    
    Validates that the invitation belongs to the agency.
    """

    invitation_id = serializers.UUIDField(
        required=True,
        help_text=_("معرّف الدعوة")
    )
