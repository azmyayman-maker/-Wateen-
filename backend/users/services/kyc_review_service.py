"""
KYC Service Layer for Agency KYC operations.

This module contains b2b logic for agency KYC review workflows,
extracted from views to maintain proper separation of concerns.
"""
from dataclasses import dataclass
from typing import Optional

from django.db import transaction

from users.models import AgencyProfile, AgencyStatus, CustomUser, KYCAuditLog


@dataclass
class ReviewResult:
    """Result of a KYC review operation."""
    agency: AgencyProfile
    audit_log: KYCAuditLog
    action: str
    new_status: AgencyStatus


class AgencyKYCService:
    """
    Service for handling agency KYC review operations.
    
    Provides b2b logic for reviewing agency KYC applications,
    including status transitions, audit logging, and notification orchestration.
    """

    @staticmethod
    def review_agency(
        agency: AgencyProfile,
        reviewer: CustomUser,
        action: str,
        notes: str,
        ip_address: str,
        user_agent: str,
    ) -> ReviewResult:
        """
        Process a KYC review action for an agency.
        
        Args:
            agency: The agency being reviewed
            reviewer: The superadmin performing the review
            action: 'APPROVE' or 'REJECT'
            notes: Optional notes from the reviewer
            ip_address: Client IP for audit (Law 151/2020)
            user_agent: User agent string for audit
        
        Returns:
            ReviewResult containing the updated agency and audit log
        
        Raises:
            ValueError: If agency is not in PENDING status
        """
        # Validate agency is in PENDING status
        if agency.status != AgencyStatus.PENDING:
            raise ValueError(
                f"Cannot review agency in '{agency.status}' status. "
                "Only PENDING agencies can be reviewed."
            )

        # Validate action is one of the allowed values
        if action not in ('APPROVE', 'REJECT'):
            raise ValueError(f"Invalid action '{action}'. Must be 'APPROVE' or 'REJECT'.")

        # Determine new status
        new_status = (
            AgencyStatus.VERIFIED if action == 'APPROVE'
            else AgencyStatus.REJECTED
        )

        # Update agency status within atomic transaction
        with transaction.atomic():
            agency.status = new_status
            agency.save(update_fields=['status', 'updated_at'])

            # Create immutable audit log entry
            audit_log = KYCAuditLog.objects.create(
                agency=agency,
                reviewer=reviewer,
                action=action,
                notes=notes,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return ReviewResult(
            agency=agency,
            audit_log=audit_log,
            action=action,
            new_status=new_status,
        )

    @staticmethod
    def handle_resubmission(
        agency: AgencyProfile,
        reviewer: CustomUser,
        ip_address: str,
        user_agent: str,
    ) -> Optional[KYCAuditLog]:
        """
        Handle agency KYC document resubmission.
        
        When an agency with REJECTED status resubmits documents,
        this transitions the agency back to PENDING and creates an audit log.
        
        Args:
            agency: The agency resubmitting documents
            reviewer: The user performing the resubmission (agency admin)
            ip_address: Client IP for audit
            user_agent: User agent string for audit
        
        Returns:
            KYCAuditLog if status was changed, None otherwise
        """
        # Check if agency was REJECTED and needs to transition back to PENDING
        if agency.status != AgencyStatus.REJECTED:
            return None

        # Transition back to PENDING within atomic transaction
        with transaction.atomic():
            agency.status = AgencyStatus.PENDING
            agency.save(update_fields=['status', 'updated_at'])

            # Create audit log for resubmission
            audit_log = KYCAuditLog.objects.create(
                agency=agency,
                reviewer=reviewer,
                action=KYCAuditLog.ActionChoices.RESUBMIT,
                notes='Documents resubmitted after rejection',
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return audit_log
