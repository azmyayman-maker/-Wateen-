from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import AgencyProfile, NurseInvitation, NurseProfile, UserRole

class NurseInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Nurse Invitation.
    Will be used by the Agency Admin to invite a nurse.
    """
    class Meta:
        model = NurseInvitation
        fields = ["id", "agency", "phone", "token", "status", "expires_at", "created_at"]
        read_only_fields = ["id", "agency", "token", "status", "expires_at", "created_at"]

class NurseProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for NurseProfile binding.
    Enforces that a nurse is assigned strictly to an agency and prevents IDOR.
    """
    class Meta:
        model = NurseProfile
        fields = [
            "agency",
            "national_id_document",
            "syndicate_number"
        ]

    def validate_agency(self, value: AgencyProfile):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError(_("Request context is missing."))

        user = request.user
        
        # IDOR PREVENTION:
        if user.role != UserRole.AGENCY_ADMIN:
            raise serializers.ValidationError(_("Only an Agency Admin can assign a nurse to an agency."))
        
        # Explicitly check that the authenticated user actually manages this agency
        if getattr(user, "agency", None) != value:
            raise serializers.ValidationError(_("You can only assign nurses to your own agency."))

        return value
