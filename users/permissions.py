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
    """Allow access only to AGENCY_ADMIN users."""

    message = 'يجب أن يكون لديك صلاحيات مدير الوكالة'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_agency_admin
        )


class IsAgencyAdminOrSuperAdmin(BasePermission):
    """Allow access to AGENCY_ADMIN or SUPERADMIN users."""

    message = 'يجب أن يكون لديك صلاحيات مدير وكالة أو مدير النظام'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.is_agency_admin or request.user.is_superadmin


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
