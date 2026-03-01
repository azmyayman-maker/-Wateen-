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


class NurseInvitationService:
    @staticmethod
    def accept_invitation(token_str, password, phone_number, email, national_id, syndicate_number, first_name, last_name):
        try:
            token_uuid = uuid.UUID(token_str)
        except ValueError:
            raise DjangoValidationError("Invalid token format.", code="invalid_format")

        # Initial check without lock to handle expiry without rolling back
        invitation = NurseInvitation.objects.filter(
            token=token_uuid,
            status=InvitationStatus.PENDING
        ).first()

        if not invitation:
            raise DjangoValidationError("Invalid or already consumed invitation token.", code="invalid_token")

        if not invitation.is_valid:
            # We can save this safely now since we are not in an atomic block that will rollback
            invitation.status = InvitationStatus.EXPIRED
            invitation.save(update_fields=["status"])
            raise DjangoValidationError("Invitation has expired.", code="expired_token")

        # Now enter the atomic transaction for creation and locking
        with transaction.atomic():
            # Re-fetch with lock to prevent race conditions
            invitation = NurseInvitation.objects.select_for_update().filter(
                token=token_uuid,
                status=InvitationStatus.PENDING
            ).first()

            if not invitation:
                raise DjangoValidationError("Invalid or already consumed invitation token.", code="invalid_token")

            # Strict validation: Ensure phone matches invitation
            if invitation.phone != phone_number:
                raise DjangoValidationError("Phone number does not match the invitation.", code="phone_mismatch")

            validate_password(password)

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

            invitation.status = InvitationStatus.ACCEPTED
            invitation.save(update_fields=["status"])

            return user, invitation.agency


class AcceptNurseInvitationView(APIView):
    """
    Endpoint for a prospective nurse to consume an invitation token,
    create their account, and securely bind to the agency.
    """
    permission_classes = [AllowAny]

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

        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        try:
            user, agency = NurseInvitationService.accept_invitation(
                token_str=token_str,
                password=password,
                phone_number=phone_number,
                email=email,
                national_id=national_id,
                syndicate_number=syndicate_number,
                first_name=first_name,
                last_name=last_name
            )
        except DjangoValidationError as e:
            if hasattr(e, "code"):
                if e.code == "invalid_token":
                    return Response({"detail": e.message}, status=status.HTTP_404_NOT_FOUND)
                elif e.code == "expired_token":
                    return Response({"detail": e.message}, status=status.HTTP_410_GONE)
            
            messages = e.messages if hasattr(e, "messages") else [str(e)]
            return Response({"detail": messages}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.exception("Failed to register nurse: IntegrityError")
            return Response(
                {"detail": "A user with this national_id or phone already exists."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Failed to register nurse")
            return Response({"detail": "Failed to register nurse"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Nurse registration successful",
                "user_id": str(user.id),
                "agency_id": str(agency.id)
            },
            status=status.HTTP_201_CREATED
        )
