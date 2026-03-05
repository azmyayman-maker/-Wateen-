from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    RegisterView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
    LoginView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    KYCUploadView,
)
from .agency_views import (
    AgencyRegisterView, 
    AgencyApprovalView, 
    AgencyKYCResubmitView,
    AgencyKYCDocumentsListView,
    KYCAuditLogListView,
    KYCQueueListView,
    KYCReviewView
)
from .coverage_views import AgencyCoverageUpdateView
from .nurse_views import (
    InviteNurseView,
    AcceptNurseInvitationView,
    InvitationListView,
    RevokeInvitationView,
    AgencyCapacityView,
    InvitationLimitsView,
)

app_name = 'users'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/accept-invitation/', AcceptNurseInvitationView.as_view(), name='accept_invitation'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # KYC document upload for nurse verification
    path('kyc/upload/', KYCUploadView.as_view(), name='kyc_upload'),
    
    # B2B Agency Onboarding & KYC
    path('agency/register/', AgencyRegisterView.as_view(), name='agency_register'),
    path('agency/kyc/resubmit/', AgencyKYCResubmitView.as_view(), name='agency_kyc_resubmit'),
    path('agency/kyc/documents/', AgencyKYCDocumentsListView.as_view(), name='agency_kyc_list'),
    path('agency/<uuid:pk>/coverage/', AgencyCoverageUpdateView.as_view(), name='agency_coverage'),
    
    # Nurse Invitation Management (Agency Admin)
    path('agency/invitations/', InviteNurseView.as_view(), name='invite_nurse'),
    path('agency/invitations/list/', InvitationListView.as_view(), name='invitation_list'),
    path('agency/invitations/<uuid:invitation_id>/revoke/', RevokeInvitationView.as_view(), name='revoke_invitation'),
    
    # Agency Capacity and Rate Limit Info
    path('agency/capacity/', AgencyCapacityView.as_view(), name='agency_capacity'),
    path('agency/invitation-limits/', InvitationLimitsView.as_view(), name='invitation_limits'),
    
    # Admin endpoints
    path('admin/agencies/<uuid:pk>/approve/', AgencyApprovalView.as_view(), name='agency_approve'),
    path('admin/agencies/<uuid:pk>/review/', KYCReviewView.as_view(), name='kyc-review'),
    path('admin/agencies/<uuid:agency_id>/kyc-audit-logs/', KYCAuditLogListView.as_view(), name='kyc-audit-logs'),
    path('admin/kyc-queue/', KYCQueueListView.as_view(), name='kyc-queue'),
]