from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    RegisterView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    KYCUploadView,
)
from .agency_views import AgencyRegisterView, AgencyApprovalView
from .coverage_views import AgencyCoverageUpdateView
from .nurse_views import InviteNurseView, AcceptNurseInvitationView

app_name = 'users'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/accept-invitation/', AcceptNurseInvitationView.as_view(), name='accept_invitation'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # KYC document upload for nurse verification
    path('kyc/upload/', KYCUploadView.as_view(), name='kyc_upload'),
    
    # B2B Agency Onboarding
    path('agency/register/', AgencyRegisterView.as_view(), name='agency_register'),
    path('agency/<uuid:pk>/coverage/', AgencyCoverageUpdateView.as_view(), name='agency_coverage'),
    path('agency/invite-nurse/', InviteNurseView.as_view(), name='invite_nurse'),
    path('admin/agencies/<uuid:pk>/approve/', AgencyApprovalView.as_view(), name='agency_approve'),
]