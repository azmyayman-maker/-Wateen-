from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
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
            
            return Response({
                'message': _('تم تسجيل الخروج بنجاح')
            }, status=status.HTTP_200_OK)
        
        except (TokenError, InvalidToken):
            return Response({
                'message': _('تم تسجيل الخروج بنجاح')
            }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    # Set the serializer to our custom version that embeds agency_id
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            serializer = TokenObtainPairResponseSerializer(data=response.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            serializer = TokenRefreshResponseSerializer(data=response.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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