"""
Nurse Invitation Service for Wateen B2B2C Platform.

Implements the core business logic for:
- Creating invitations with SaaS capacity validation
- Accepting invitations with atomic user/profile creation
- Token validation and lifecycle management

B2B2C Rules Enforced:
- Nurses must belong to an agency (never freelancers)
- Agency capacity is enforced via network_capacity field
- All invitations are scoped to the agency tenant
"""

import logging
import uuid
from datetime import timedelta
from decimal import Decimal
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..models import (
    NurseInvitation,
    CustomUser,
    NurseProfile,
    AgencyProfile,
    UserRole,
    InvitationStatus,
)
from .rate_limiting import get_invitation_rate_limiter

logger = logging.getLogger(__name__)


class InvitationError(Exception):
    """Base exception for invitation-related errors."""
    
    def __init__(self, message: str, code: str = "invitation_error"):
        self.message = message
        self.code = code
        super().__init__(message)


class CapacityExceededError(InvitationError):
    """Raised when agency has reached maximum nurse capacity."""
    
    def __init__(self, message: str):
        super().__init__(message, code="capacity_exceeded")


class RateLimitExceededError(InvitationError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, code="rate_limited")


class InvalidTokenError(InvitationError):
    """Raised when invitation token is invalid or expired."""
    
    def __init__(self, message: str, code: str = "invalid_token"):
        super().__init__(message, code=code)


class DuplicateUserError(InvitationError):
    """Raised when user already exists (national_id or phone conflict)."""
    
    def __init__(self, message: str):
        super().__init__(message, code="already_registered")


class InvitationService:
    """
    Service class for nurse invitation operations.
    
    Handles:
    - Invitation creation with capacity and rate limit checks
    - Invitation acceptance with atomic user creation
    - Token validation and lifecycle management
    """
    
    # Invitation expiry time in hours
    INVITATION_EXPIRY_HOURS = 72
    
    @classmethod
    def create_invitation(
        cls,
        agency: AgencyProfile,
        phone: str,
        skip_rate_limit: bool = False
    ) -> NurseInvitation:
        """
        Create a new nurse invitation with validation.
        
        Steps:
        1. Check rate limit (6 invites/hour per agency)
        2. Lock agency row and validate capacity (active nurses + pending invites < capacity)
        3. Expire any existing PENDING invitations for the same phone+agency
        4. Create invitation with secure token
        
        Args:
            agency: AgencyProfile creating the invitation
            phone: Target phone number for invitation
            skip_rate_limit: Skip rate limit check (for testing)
            
        Returns:
            NurseInvitation instance
            
        Raises:
            RateLimitExceededError: If rate limit exceeded
            CapacityExceededError: If agency capacity exceeded
            InvitationError: For other validation errors
        """
        # Step 1: Rate limit check (outside transaction — read-only, idempotent)
        if not skip_rate_limit:
            rate_limiter = get_invitation_rate_limiter()
            if not rate_limiter.is_allowed(str(agency.id)):
                remaining_time = rate_limiter.get_reset_time(str(agency.id))
                raise RateLimitExceededError(
                    message=_("Invitation limit reached. Please try again later."),
                    retry_after=remaining_time
                )
        
        # Steps 2-4: Atomic block with agency lock to prevent TOCTOU capacity race
        with transaction.atomic():
            # Lock the agency row to serialize concurrent invitation creates
            AgencyProfile.objects.select_for_update().filter(id=agency.id).first()
            
            # Step 2: Capacity check (under lock)
            active_nurses = agency.nurses.count()
            pending_invitations = agency.invitations.filter(status=InvitationStatus.PENDING).count()
            total_count = active_nurses + pending_invitations
            
            if total_count >= agency.network_capacity:
                raise CapacityExceededError(
                    message=_(
                        "Agency has reached maximum capacity (%(capacity)d nurses). "
                        "Please upgrade your plan or remove inactive nurses."
                    ) % {"capacity": agency.network_capacity}
                )
            
            # Step 3: Expire existing PENDING invitations for the same phone+agency
            expired_count = NurseInvitation.objects.filter(
                agency=agency,
                phone=phone,
                status=InvitationStatus.PENDING
            ).update(status=InvitationStatus.EXPIRED)
            if expired_count > 0:
                logger.info(f"Auto-expired {expired_count} old invitation(s) for phone {phone[:3]}***{phone[-4:]}")
            
            # Step 4: Create invitation
            expires_at = timezone.now() + timedelta(hours=cls.INVITATION_EXPIRY_HOURS)
            
            invitation = NurseInvitation.objects.create(
                agency=agency,
                phone=phone,
                expires_at=expires_at,
                status=InvitationStatus.PENDING
            )
        
        logger.info(
            f"Created invitation {invitation.id} for agency {agency.id}, "
            f"phone {phone[:3]}***{phone[-4:]}, expires at {expires_at}"
        )
        
        return invitation
    
    @classmethod
    def validate_token(cls, token_str: str) -> NurseInvitation:
        """
        Validate an invitation token.
        
        Args:
            token_str: UUID string token
            
        Returns:
            NurseInvitation if valid
            
        Raises:
            InvalidTokenError: If token is invalid, expired, or already used
        """
        try:
            token_uuid = uuid.UUID(token_str)
        except ValueError:
            raise InvalidTokenError(_("Invalid token format."), code="invalid_format")
        
        invitation = NurseInvitation.objects.filter(token=token_uuid).first()
        
        if not invitation:
            raise InvalidTokenError(_("Invalid invitation token."), code="invalid_token")
        
        if invitation.status == InvitationStatus.ACCEPTED:
            raise InvalidTokenError(_("This invitation has already been used."), code="already_used")
        
        if invitation.status == InvitationStatus.REVOKED:
            raise InvalidTokenError(_("This invitation has been revoked."), code="revoked")
        
        if invitation.status == InvitationStatus.EXPIRED or not invitation.is_valid:
            raise InvalidTokenError(_("This invitation has expired."), code="expired_token")
        
        return invitation
    
    @classmethod
    def accept_invitation(
        cls,
        token_str: str,
        password: str,
        phone_number: str,
        national_id: str,
        syndicate_number: str,
        first_name: str = "",
        last_name: str = "",
        email: str = ""
    ) -> tuple[CustomUser, AgencyProfile]:
        """
        Accept a nurse invitation and create the user account.
        
        Atomic operation that:
        1. Validates the token
        2. Creates the user with NURSE role
        3. Creates the nurse profile bound to the agency
        4. Marks the invitation as ACCEPTED
        
        Args:
            token_str: Invitation token UUID string
            password: User password
            phone_number: User phone number (must match invitation)
            national_id: Egyptian national ID (14 digits)
            syndicate_number: Nursing syndicate membership number
            first_name: Arabic first name
            last_name: Arabic last name
            email: Optional email address
            
        Returns:
            Tuple of (CustomUser, AgencyProfile)
            
        Raises:
            InvalidTokenError: If token is invalid or expired
            DuplicateUserError: If user with national_id/phone already exists
            InvitationError: For other errors
        """
        # Pre-lock validation (fast-fail for invalid/expired tokens)
        invitation = cls.validate_token(str(token_str))
        
        # Atomic transaction for user creation
        try:
            with transaction.atomic():
                # Re-fetch with lock to prevent race conditions
                invitation = NurseInvitation.objects.select_for_update().filter(
                    token=invitation.token,
                    status=InvitationStatus.PENDING
                ).first()
                
                if not invitation:
                    raise InvalidTokenError(
                        _("Invalid or already consumed invitation token."),
                        code="invalid_token"
                    )
                
                # W1: Phone match check inside atomic block (prevents timing leak)
                if invitation.phone != phone_number:
                    raise InvalidTokenError(
                        _("Phone number does not match the invitation."),
                        code="phone_mismatch"
                    )
                
                # Create user
                user = CustomUser.objects.create_user(
                    national_id=national_id,
                    phone_number=phone_number,
                    password=password,
                    email=email or None,
                    role=UserRole.NURSE,
                    first_name_ar=first_name,
                    last_name_ar=last_name
                )
                
                # Create nurse profile bound to agency (B2B2C rule)
                # skip_full_clean=True: agency is already validated from invitation
                _profile = NurseProfile(
                    user=user,
                    agency=invitation.agency,
                    syndicate_number=syndicate_number
                )
                _profile.save(skip_full_clean=True)
                
                # Mark invitation as accepted
                invitation.status = InvitationStatus.ACCEPTED
                invitation.save(update_fields=["status"])
                
                logger.info(
                    f"Nurse {user.id} registered via invitation {invitation.id}, "
                    f"bound to agency {invitation.agency.id}"
                )
                
                return user, invitation.agency
                
        except IntegrityError as e:
            logger.exception(f"IntegrityError during nurse registration: {e}")
            raise DuplicateUserError(
                _("A user with this national_id or phone already exists.")
            )
        except InvitationError:
            # Re-raise specific errors (InvalidTokenError, etc.) without wrapping
            raise
        except Exception as e:
            logger.exception(f"Failed to register nurse: {e}")
            raise InvitationError(_("Failed to register nurse. Please try again."))
    
    @classmethod
    def revoke_invitation(
        cls,
        invitation_id: uuid.UUID,
        agency: AgencyProfile
    ) -> bool:
        """
        Revoke a pending invitation.
        
        Only the agency that created the invitation can revoke it.
        
        Args:
            invitation_id: UUID of the invitation to revoke
            agency: AgencyProfile attempting to revoke
            
        Returns:
            True if successfully revoked
            
        Raises:
            InvitationError: If invitation not found or cannot be revoked
        """
        invitation = NurseInvitation.objects.filter(
            id=invitation_id,
            agency=agency
        ).first()
        
        if not invitation:
            raise InvitationError(_("Invitation not found."))
        
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationError(
                _("Only pending invitations can be revoked."),
                code="invalid_status"
            )
        
        invitation.status = InvitationStatus.REVOKED
        invitation.save(update_fields=["status"])
        
        logger.info(f"Invitation {invitation_id} revoked by agency {agency.id}")
        
        return True
    
    @classmethod
    def get_agency_invitations(
        cls,
        agency: AgencyProfile,
        status_filter: str = None
    ) -> list[NurseInvitation]:
        """
        Get all invitations for an agency.
        
        Args:
            agency: AgencyProfile to get invitations for
            status_filter: Optional status filter (PENDING, ACCEPTED, EXPIRED, REVOKED)
            
        Returns:
            QuerySet of NurseInvitation instances
        """
        queryset = NurseInvitation.objects.filter(agency=agency)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by("-created_at")
    
    @classmethod
    def expire_old_invitations(cls) -> int:
        """
        Mark all expired invitations as EXPIRED.
        
        Background task to clean up invitations past their expiry date.
        
        Returns:
            Number of invitations marked as expired
        """
        expired_count = NurseInvitation.objects.filter(
            status=InvitationStatus.PENDING,
            expires_at__lt=timezone.now()
        ).update(status=InvitationStatus.EXPIRED)
        
        if expired_count > 0:
            logger.info(f"Marked {expired_count} invitations as expired")
        
        return expired_count