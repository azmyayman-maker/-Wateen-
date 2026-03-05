"""
DRF Permission Classes for Wateen B2B2C RBAC.

These replace the broken RBACMiddleware and run AFTER JWT authentication,
solving the timing issue where middleware runs before DRF authenticates.

Usage in views:
    from users.permissions import IsSuperAdmin, IsAgencyAdmin

    class AgencyApprovalView(APIView):
        permission_classes = [IsAuthenticated, IsSuperAdmin]
"""

from rest_framework.permissions import BasePermission
from users.models import AgencyStatus


class IsSuperAdmin(BasePermission):
    """Allow access only to SUPERADMIN users."""

    message = 'يجب أن يكون لديك صلاحيات مدير النظام'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superadmin
        )


class IsAgencyAdmin(BasePermission):
    """
    Allow access only to AGENCY_ADMIN users with a verified agency.
    
    FR-001: Grants access ONLY to authenticated users with role=AGENCY_ADMIN
    AND a verified AgencyProfile (status=VERIFIED).
    FR-002: Handles missing AgencyProfile gracefully without raising 500 errors.
    """

    message = 'يجب أن يكون لديك صلاحيات مدير وكالة موثقة'

    def has_permission(self, request, view):
        # Check basic authentication
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check user has AGENCY_ADMIN role
        if not request.user.is_agency_admin:
            return False
        
        # Check agency exists and is verified (FR-001, FR-002)
        agency = getattr(request.user, 'agency', None)
        if agency is None:
            return False
        
        return agency.status == AgencyStatus.VERIFIED


class IsAgencyAdminAnyStatus(BasePermission):
    """
    Allow access to AGENCY_ADMIN users regardless of agency verification status.
    Required for endpoints like KYC documents resubmission where agency might be PENDING or REJECTED.
    """

    message = 'يجب أن تكون مديراً لوكالة'

    def has_permission(self, request, view):
        # Check basic authentication
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check user has AGENCY_ADMIN role
        if not request.user.is_agency_admin:
            return False
        
        # Check agency exists
        agency = getattr(request.user, 'agency', None)
        if agency is None:
            return False
            
        return True


class IsAgencyAdminOrSuperAdmin(BasePermission):
    """
    Allow access to AGENCY_ADMIN with verified agency OR SUPERADMIN users.
    
    SUPERADMIN bypasses the agency check.
    """

    message = 'يجب أن يكون لديك صلاحيات مدير وكالة أو مدير النظام'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # SUPERADMIN bypasses agency check
        if request.user.is_superadmin:
            return True
        
        # AGENCY_ADMIN must have verified agency
        if not request.user.is_agency_admin:
            return False
        
        agency = getattr(request.user, 'agency', None)
        if agency is None:
            return False
        
        return agency.status == AgencyStatus.VERIFIED


class IsNurseOrAbove(BasePermission):
    """Allow access to NURSE, AGENCY_ADMIN, or SUPERADMIN users."""

    message = 'يجب أن تكون ممرض/ة أو أعلى'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return (
            request.user.is_nurse
            or request.user.is_agency_admin
            or request.user.is_superadmin
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allow access if user owns the object
    or is a SUPERADMIN.

    The view's queryset model must have a `user` FK or the object
    must be a CustomUser instance itself.
    """

    message = 'ليس لديك صلاحية الوصول لهذا المورد'

    def has_object_permission(self, request, view, obj):
        if not getattr(request, 'user', None) or not getattr(request.user, 'is_authenticated', False):
            return False
            
        # 1. Superadmins can touch anything
        if request.user.is_superadmin:
            return True
        # If the object IS a user, compare directly
        if hasattr(obj, 'national_id'):
            return obj == request.user
        # If the object has a user FK
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # If the object has a user_id field
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
        return False
