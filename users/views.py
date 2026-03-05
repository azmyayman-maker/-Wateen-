from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

from .models import CustomUser, UserRole, NurseDocument, NurseProfile
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    KYCDocumentUploadSerializer,
    NurseDocumentSerializer,
    CustomTokenObtainPairSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': _('تم تغيير كلمة المرور بنجاح')
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            response = Response({
                'message': _('تم تسجيل الخروج بنجاح')
            }, status=status.HTTP_200_OK)
        
        except (TokenError, InvalidToken):
            response = Response({
                'message': _('تم تسجيل الخروج بنجاح')
            }, status=status.HTTP_200_OK)
            
        response.delete_cookie(getattr(settings, 'JWT_AUTH_COOKIE', 'access_token'))
        response.delete_cookie(getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'refresh_token'))
        
        return response


class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Authenticates a user with national_id + password.
    Returns user profile data + JWT tokens.
    Used by the React Admin authProvider.
    """
    permission_classes = [AllowAny]

    def post(self, request):

        national_id = request.data.get('national_id')
        password = request.data.get('password')

        if not national_id or not password:
            return Response(
                {'detail': _('الرقم القومي وكلمة المرور مطلوبان.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, national_id=national_id, password=password)

        if user is None:
            return Response(
                {'detail': _('بيانات الدخول غير صحيحة.')},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'detail': _('الحساب معطّل.')},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Build user data
        user_data = {
            'id': str(user.id),
            'national_id': user.national_id,
            'phone_number': user.phone_number,
            'first_name_ar': user.first_name_ar or '',
            'last_name_ar': user.last_name_ar or '',
            'role': user.role,
            'agency': None,
        }

        # Include agency info if user is AGENCY_ADMIN
        if user.role == UserRole.AGENCY_ADMIN and hasattr(user, 'agency') and user.agency:
            user_data['agency'] = {
                'id': str(user.agency.id),
                'name': user.agency.manager_name,
            }

        response = Response({
            'user': user_data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }, status=status.HTTP_200_OK)

        cookie_max_age = getattr(settings, 'SIMPLE_JWT', {}).get('ACCESS_TOKEN_LIFETIME', 3600*24).total_seconds()
        
        response.set_cookie(
            getattr(settings, 'JWT_AUTH_COOKIE', 'access_token'),
            str(refresh.access_token),
            max_age=int(cookie_max_age),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )
        response.set_cookie(
            getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'refresh_token'),
            str(refresh),
            max_age=3600 * 24 * 7,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax'
        )
        
        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    # Set the serializer to our custom version that embeds agency_id
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            serializer = TokenObtainPairResponseSerializer(data=response.data)
            serializer.is_valid(raise_exception=True)
            res = Response(serializer.data, status=status.HTTP_200_OK)
            
            res.set_cookie(
                getattr(settings, 'JWT_AUTH_COOKIE', 'access_token'),
                response.data.get('access', ''),
                max_age=int(getattr(settings, 'SIMPLE_JWT', {}).get('ACCESS_TOKEN_LIFETIME', 3600*24).total_seconds()),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            res.set_cookie(
                getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'refresh_token'),
                response.data.get('refresh', ''),
                max_age=3600 * 24 * 7,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            return res
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            serializer = TokenRefreshResponseSerializer(data=response.data)
            serializer.is_valid(raise_exception=True)
            res = Response(serializer.data, status=status.HTTP_200_OK)
            
            res.set_cookie(
                getattr(settings, 'JWT_AUTH_COOKIE', 'access_token'),
                response.data.get('access', ''),
                max_age=int(getattr(settings, 'SIMPLE_JWT', {}).get('ACCESS_TOKEN_LIFETIME', 3600*24).total_seconds()),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            return res
        
        return response


class KYCUploadView(APIView):
    """
    POST /api/v1/kyc/upload/
    
    Upload a KYC document (National ID or Syndicate Card) for nurse verification.
    Accepts multipart/form-data with document_type and document_file.
    
    - Requires authenticated nurse user.
    - Processes image through OpenCV + Tesseract OCR.
    - Returns verification result (never a 500 error).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # ── Role check: only nurses can upload KYC documents ──
        user = request.user
        if user.role != UserRole.NURSE:
            return Response(
                {
                    'status': 'error',
                    'reason': 'Only nurses can upload KYC documents.',
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ── Validate input ──
        serializer = KYCDocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'status': 'error',
                    'reason': 'Invalid upload data.',
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document_type = serializer.validated_data['document_type']
        document_file = serializer.validated_data['document_file']

        # ── Get nurse profile ──
        try:
            nurse_profile = user.nurse_profile
        except NurseProfile.DoesNotExist:
            return Response(
                {
                    'status': 'error',
                    'reason': 'Nurse profile not found. Please complete registration first.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Create or replace existing document of the same type ──
        existing_doc = NurseDocument.objects.filter(
            nurse=nurse_profile,
            document_type=document_type,
        ).first()

        if existing_doc:
            # Delete old file to avoid storage buildup
            if existing_doc.document_file:
                existing_doc.document_file.delete(save=False)
            existing_doc.delete()

        nurse_document = NurseDocument.objects.create(
            nurse=nurse_profile,
            document_type=document_type,
            document_file=document_file,
        )

        # ── Run KYC verification (synchronous MVP) ──
        try:
            from users.services.kyc_service import verify_kyc_document

            result = verify_kyc_document(
                nurse_document=nurse_document,
                expected_national_id=user.national_id,
            )
        except Exception as e:
            logger.exception("KYC Verification failed unexpectedly: %s", e)
            # Never crash — return graceful rejection
            nurse_document.status = 'REJECTED'
            nurse_document.rejection_reason = (
                'حدث خطأ أثناء معالجة المستند. يرجى المحاولة مرة أخرى.'
            )
            nurse_document.save()
            result = {
                'status': 'rejected',
                'reason': (
                    'An error occurred while processing the document. '
                    'Please try again.'
                ),
                'extracted_id': None,
            }

        # ── Build response ──
        response_data = {
            'status': result['status'],
            'reason': result['reason'],
            'document': NurseDocumentSerializer(nurse_document).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)