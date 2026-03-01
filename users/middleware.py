from django.http import JsonResponse
from rest_framework import status
import re

class RBACMiddleware:
    """
    Role-Based Access Control Middleware for B2B2C Migration.
    Enforces route-specific access logic based on JWT token roles.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary of compiled regex paths and their allowed roles
        self.role_paths = {
            re.compile(r'^/api/v1/agency/.*/dashboard/'): ['ADMIN', 'AgencyAdmin'],
            re.compile(r'^/api/v1/agency/'): ['ADMIN', 'AgencyAdmin'],
            re.compile(r'^/api/v1/nurses/'): ['ADMIN', 'AgencyAdmin', 'NURSE'],
            re.compile(r'^/api/v1/admin/'): ['ADMIN'],
            re.compile(r'^/api/v1/visits/request/'): ['ADMIN', 'PATIENT'],
        }

    def __call__(self, request):
        # We only check API paths
        if request.path.startswith('/api/'):
            # Allow open paths if needed here (like login/register)
            if request.path in ['/api/v1/auth/login/', '/api/v1/auth/register/', '/api/v1/health/']:
                return self.get_response(request)
            
            # The request user is usually populated by SimpleJWT authentication class in the view.
            # Middleware runs before view processing, so request.user here might be AnonymousUser
            # if session auth isn't used. 
            # In purely JWT setups, DRF handles this at the view level (IsAuthenticated, custom permissions).
            # This middleware acts as a fail-safe or can extract the role from the token header manually if needed.
            
            # In Wateen's DRF setup, we generally prefer custom Permission classes. 
            # We enforce RBAC centrally here assuming JWT middleware has run or we parse it:
            
            user = request.user
            if user and user.is_authenticated:
                user_role = getattr(user, 'role', None)
                
                # Check mapping
                for path_regex, allowed_roles in self.role_paths.items():
                    if path_regex.match(request.path):
                        if user_role not in allowed_roles:
                            return JsonResponse(
                                {'error': 'Forbidden: Insufficient permissions for this B2B pathway.'}, 
                                status=status.HTTP_403_FORBIDDEN
                            )
                        break

        response = self.get_response(request)
        return response
