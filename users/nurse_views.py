"""
Nurse Invitation Views for Wateen B2B2C Platform.

Implements the API endpoints for:
- Agency Admin inviting nurses (InviteNurseView)
- Prospective nurses accepting invitations (AcceptNurseInvitationView)
- Agency Admin managing invitations (InvitationListView, RevokeInvitationView)
- Agency capacity info (AgencyCapacityView)

B2B2C Rules Enforced:
- Only Agency Admins can invite nurses
- Nurses are bound to the inviting agency (never freelancers)
- Rate limiting prevents SMS/Email bombing
- SaaS capacity limits are enforced
"""

import logging
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import SimpleRateThrottle

from .models import NurseInvitation, InvitationStatus
from .permissions import IsAgencyAdmin
from .nurse_serializers import (
    NurseInvitationSerializer,
    NurseInvitationCreateResponseSerializer,
    NurseInvitationCreateSerializer,
    AcceptInvitationSerializer,
)
from .services.invitation import (
    InvitationService,
    InvitationError,
    CapacityExceededError,
    RateLimitExceededError,
    InvalidTokenError,
    DuplicateUserError,
)
from .services.rate_limiting import get_invitation_rate_limiter
from .tasks import send_nurse_invitation_task

logger = logging.getLogger(__name__)


class AcceptInvitationThrottle(SimpleRateThrottle):
    """
    Throttle for the public accept-invitation endpoint.
    
    Prevents brute-force token guessing by limiting requests per IP.
    Always keys on client IP regardless of authentication status,
    so attackers cannot bypass by sending an Authorization header.
    10 requests per minute per IP address.
    """
    rate = '10/min'
    
    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope or 'accept_invitation',
            'ident': self.get_ident(request),
        }


class InviteNurseView(APIView):
    """
    Endpoint for Agency Admins to invite a new nurse.
    
    Creates a cryptographically secure token valid for 72 hours.
    Enforces:
    - Rate limiting (6 invitations per hour per agency)
    - SaaS capacity limits (network_capacity)
    
    POST /api/v1/agencies/nurses/invite/
    
    Request Body:
        {
            "phone": "01001234567"
        }
    
    Response (201 Created):
        {
            "id": "uuid",
            "phone": "01001234567",
            "token": "uuid",
            "status": "PENDING",
            "expires_at": "2026-03-08T18:00:00Z",
            "created_at": "2026-03-05T18:00:00Z"
        }
    
    Response (429 Too Many Requests):
        {
            "detail": "Invitation limit reached. Please try again later.",
            "code": "rate_limited",
            "retry_after": 3600
        }
    
    Response (402 Payment Required):
        {
            "detail": "Agency has reached maximum capacity.",
            "code": "capacity_exceeded"
        }
    """
    permission_classes = [IsAuthenticated, IsAgencyAdmin]

    def post(self, request: HttpRequest) -> HttpResponse:
        # Validate agency association
        agency = getattr(request.user, "agency", None)
        if not agency:
            return Response(
                {"detail": "You do not have an associated verified agency."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate request data
        serializer = NurseInvitationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data["phone"]

        try:
            # Create invitation with rate limiting and capacity checks
            invitation = InvitationService.create_invitation(
                agency=agency,
                phone=phone
            )
            
            # Dispatch async notification task
            send_nurse_invitation_task.delay(str(invitation.id))
            
            # Return invitation data
            # Use create-response serializer (includes token) — NOT the list serializer
            response_serializer = NurseInvitationCreateResponseSerializer(invitation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except RateLimitExceededError as e:
            logger.warning(f"Rate limit exceeded for agency {agency.id}: {e.message}")
            response_data = {
                "detail": str(e.message),
                "code": e.code,
            }
            if e.retry_after:
                response_data["retry_after"] = e.retry_after
            return Response(response_data, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
        except CapacityExceededError as e:
            logger.warning(f"Capacity exceeded for agency {agency.id}: {e.message}")
            return Response(
                {"detail": str(e.message), "code": e.code},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )
            
        except InvitationError as e:
            logger.error(f"Invitation error for agency {agency.id}: {e.message}")
            return Response(
                {"detail": str(e.message), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )


class AcceptNurseInvitationView(APIView):
    """
    Endpoint for a prospective nurse to accept an invitation.
    
    Creates the user account and binds the nurse to the agency.
    Public endpoint (no authentication required).
    
    POST /api/v1/auth/accept-invitation/
    
    Request Body:
        {
            "token": "uuid",
            "password": "securepassword123",
            "national_id": "29001011234567",
            "phone": "01001234567",
            "syndicate_number": "123456",
            "full_name": "محمد أحمد"
        }
    
    Response (201 Created):
        {
            "message": "Nurse registration successful",
            "user_id": "uuid",
            "agency_id": "uuid"
        }
    
    Response (409 Conflict):
        {
            "detail": "A user with this national_id or phone already exists.",
            "code": "already_registered"
        }
    
    Response (410 Gone):
        {
            "detail": "Invitation has expired.",
            "code": "expired_token"
        }
    """
    permission_classes = [AllowAny]
    throttle_classes = [AcceptInvitationThrottle]

    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = AcceptInvitationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        
        # Parse full name
        full_name = data.get("full_name", "")
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        try:
            user, agency = InvitationService.accept_invitation(
                token_str=data["token"],
                password=data["password"],
                phone_number=data["phone"],
                national_id=data["national_id"],
                syndicate_number=data["syndicate_number"],
                first_name=first_name,
                last_name=last_name,
                email=data.get("email", "")
            )
            
            return Response(
                {
                    "message": "Nurse registration successful",
                    "user_id": str(user.id),
                    "agency_id": str(agency.id)
                },
                status=status.HTTP_201_CREATED
            )
            
        except InvalidTokenError as e:
            logger.warning(f"Invalid invitation token: {e.message}")
            
            if e.code == "expired_token":
                return Response(
                    {"detail": str(e.message), "code": e.code},
                    status=status.HTTP_410_GONE
                )
            elif e.code == "already_used":
                return Response(
                    {"detail": str(e.message), "code": e.code},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"detail": str(e.message), "code": e.code},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except DuplicateUserError as e:
            logger.warning(f"Duplicate user registration attempt: {e.message}")
            return Response(
                {"detail": str(e.message), "code": e.code},
                status=status.HTTP_409_CONFLICT
            )
            
        except InvitationError as e:
            logger.error(f"Invitation acceptance error: {e.message}")
            return Response(
                {"detail": str(e.message), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )


class InvitationListView(APIView):
    """
    List all invitations for the authenticated agency.
    
    GET /api/v1/agencies/invitations/
    GET /api/v1/agencies/invitations/?status=PENDING
    
    Response (200 OK):
        [
            {
                "id": "uuid",
                "phone": "01001234567",
                "status": "PENDING",
                "expires_at": "...",
                "created_at": "..."
            }
        ]
    """
    permission_classes = [IsAuthenticated, IsAgencyAdmin]

    def get(self, request: HttpRequest) -> HttpResponse:
        agency = getattr(request.user, "agency", None)
        if not agency:
            return Response(
                {"detail": "You do not have an associated verified agency."},
                status=status.HTTP_403_FORBIDDEN
            )

        status_filter = request.query_params.get("status")
        
        # S1: Validate status filter against known values
        valid_statuses = {s.value for s in InvitationStatus}
        if status_filter and status_filter not in valid_statuses:
            return Response(
                {"detail": f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitations = InvitationService.get_agency_invitations(
            agency=agency,
            status_filter=status_filter
        )
        
        serializer = NurseInvitationSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RevokeInvitationView(APIView):
    """
    Revoke a pending invitation.
    
    Only the agency that created the invitation can revoke it.
    
    POST /api/v1/agencies/invitations/<id>/revoke/
    
    Response (200 OK):
        {
            "detail": "Invitation revoked successfully."
        }
    """
    permission_classes = [IsAuthenticated, IsAgencyAdmin]

    def post(self, request: HttpRequest, invitation_id: str) -> HttpResponse:
        agency = getattr(request.user, "agency", None)
        if not agency:
            return Response(
                {"detail": "You do not have an associated verified agency."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            InvitationService.revoke_invitation(
                invitation_id=invitation_id,
                agency=agency
            )
            return Response(
                {"detail": "Invitation revoked successfully."},
                status=status.HTTP_200_OK
            )
        except InvitationError as e:
            return Response(
                {"detail": str(e.message), "code": e.code},
                status=status.HTTP_400_BAD_REQUEST
            )





class AgencyCapacityView(APIView):
    """
    Get agency capacity information for UI display.
    
    Returns current nurse count, pending invitations, and capacity limits.
    Used by the React Admin dashboard for warning modals.
    
    GET /api/v1/agency/capacity/
    
    Response (200 OK):
        {
            "used": 5,
            "pending": 2,
            "total": 10,
            "available": 3
        }
    """
    permission_classes = [IsAuthenticated, IsAgencyAdmin]
    
    def get(self, request: HttpRequest) -> HttpResponse:
        agency = getattr(request.user, "agency", None)
        if not agency:
            return Response(
                {"detail": "You do not have an associated verified agency."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_nurses = agency.nurses.count()
        pending_invitations = agency.invitations.filter(status=InvitationStatus.PENDING).count()
        total_capacity = agency.network_capacity
        used = active_nurses + pending_invitations
        available = max(0, total_capacity - used)
        
        return Response({
            "used": used,
            "pending": pending_invitations,
            "total": total_capacity,
            "available": available
        }, status=status.HTTP_200_OK)


class InvitationLimitsView(APIView):
    """
    Get invitation rate limit information for UI display.
    
    Returns remaining invitations in current window and reset time.
    Used by the React Admin dashboard for rate limit warnings.
    
    GET /api/v1/agency/invitation-limits/
    
    Response (200 OK):
        {
            "remaining": 4,
            "max_per_hour": 6,
            "reset_time": 1700000000
        }
    """
    permission_classes = [IsAuthenticated, IsAgencyAdmin]
    
    def get(self, request: HttpRequest) -> HttpResponse:
        agency = getattr(request.user, "agency", None)
        if not agency:
            return Response(
                {"detail": "You do not have an associated verified agency."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rate_limiter = get_invitation_rate_limiter()
        remaining = rate_limiter.get_remaining(str(agency.id))
        reset_time = rate_limiter.get_reset_time(str(agency.id))
        
        return Response({
            "remaining": remaining,
            "max_per_hour": rate_limiter.MAX_INVITATIONS_PER_HOUR,
            "reset_time": reset_time
        }, status=status.HTTP_200_OK)
