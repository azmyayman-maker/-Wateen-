import logging
import uuid
from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction, IntegrityError
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import NurseInvitation, CustomUser, NurseProfile, UserRole, InvitationStatus
from .permissions import IsAgencyAdmin
from .nurse_serializers import NurseInvitationSerializer

logger = logging.getLogger(__name__)


class InviteNurseView(APIView):
    """
    Endpoint for Agency Admins to invite a new nurse.
    Creates a cryptographically secure token valid for 72 hours.
    """
    permission_classes = [IsAuthenticated, IsAgencyAdmin]

    def post(self, request: HttpRequest) -> HttpResponse:
        agency = getattr(request.user, "agency", None)
        if not agency:
            return Response(
                {"detail": "You do not have an associated verified agency."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        phone = request.data.get("phone")
        if not phone:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        expires_at = timezone.now() + timedelta(hours=72)
        
        invitation = NurseInvitation.objects.create(
            agency=agency,
            phone=phone,
            expires_at=expires_at
        )
        
        serializer = NurseInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptNurseInvitationView(APIView):
    """
    Endpoint for a prospective nurse to consume an invitation token,
    create their account, and securely bind to the agency.
    """
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request: HttpRequest) -> HttpResponse:
        token_str = request.data.get("token")
        password = request.data.get("password")
        
        phone_number = request.data.get("phone", "")
        email = request.data.get("email", "")
        national_id = request.data.get("national_id", "")
        syndicate_number = request.data.get("syndicate_number", "")
        full_name = request.data.get("full_name", "")

        if not token_str or not password or not national_id or not phone_number or not syndicate_number:
            return Response(
                {"detail": "token, password, national_id, syndicate_number and phone are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_uuid = uuid.UUID(token_str)
        except ValueError:
            return Response({"detail": "Invalid token format."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch and validate the invitation
        try:
            invitation = NurseInvitation.objects.select_for_update().get(
                token=token_uuid, 
                status=InvitationStatus.PENDING
            )
        except NurseInvitation.DoesNotExist:
            return Response({"detail": "Invalid or already consumed invitation token."}, status=status.HTTP_400_BAD_REQUEST)

        if not invitation.is_valid:
            invitation.status = InvitationStatus.EXPIRED
            invitation.save()
            return Response({"detail": "Invitation has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validate password
        try:
            validate_password(password)
        except DjangoValidationError as e:
            return Response({"detail": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create CustomUser & NurseProfile atomically
        try:
            # Split full name into first and last roughly
            name_parts = full_name.split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            user = CustomUser.objects.create_user(
                national_id=national_id,
                phone_number=phone_number,
                password=password,
                email=email,
                role=UserRole.NURSE,
                first_name_ar=first_name,
                last_name_ar=last_name
            )

            _profile = NurseProfile.objects.create(
                user=user,
                agency=invitation.agency,
                syndicate_number=syndicate_number
            )

            # Mark invitation as accepted
            invitation.status = InvitationStatus.ACCEPTED
            invitation.save()

        except IntegrityError as e:
            transaction.set_rollback(True)
            return Response({"detail": "A user with this national_id or phone already exists.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.set_rollback(True)
            logger.exception("Failed to register nurse")
            return Response({"detail": "Failed to register nurse"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Nurse registration successful",
                "user_id": str(user.id),
                "agency_id": str(invitation.agency.id)
            },
            status=status.HTTP_201_CREATED
        )
