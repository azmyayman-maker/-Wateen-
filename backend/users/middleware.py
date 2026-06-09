"""
DEPRECATED: This middleware has been replaced by DRF permission classes.

The RBACMiddleware had three critical flaws:
1. Used legacy role names (ADMIN/AgencyAdmin) that don't match UserRole enum
2. JWT authentication happens at the view level, not middleware level
3. request.user is always AnonymousUser when middleware runs for JWT requests

Use users.permissions instead:
    from users.permissions import IsSuperAdmin, IsAgencyAdmin

See: users/permissions.py
"""
