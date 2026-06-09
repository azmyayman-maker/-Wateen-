from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import CustomUser, UserRole
from .validators import validate_egyptian_national_id, validate_phone_number

User = get_user_model()


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Serializer to embed B2B2C specific claims like role and agency_id.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role

        # Add agency context if available
        # For nurses: check nurse_profile.agency_id
        if hasattr(user, 'nurse_profile') and user.nurse_profile and user.nurse_profile.agency_id:
            token['agency_id'] = str(user.nurse_profile.agency_id)
        # For agency admins: check user.agency directly (added to CustomUser model)
        elif hasattr(user, 'agency') and user.agency_id:
            token['agency_id'] = str(user.agency_id)

        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer with role escalation prevention.
    
    FR-005: Limits self-registration to PATIENT and AGENCY_ADMIN only.
    FR-006: Rejects SUPERADMIN and NURSE roles with Arabic validation errors.
    """

    # Roles allowed for self-registration (FR-005)
    SELF_REGISTRATION_ROLES = {UserRole.PATIENT, UserRole.AGENCY_ADMIN}

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_('كلمة المرور')
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_('تأكيد كلمة المرور')
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'national_id',
            'phone_number',
            'email',
            'password',
            'password_confirm',
            'role',
            'first_name_ar',
            'last_name_ar'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'national_id': {'required': True},
            'phone_number': {'required': True},
            'email': {'required': False},
            'role': {'required': False},
            'first_name_ar': {'required': False},
            'last_name_ar': {'required': False}
        }

    def validate_role(self, value):
        """
        Validate role field to prevent privilege escalation (FR-005, FR-006).
        
        Only PATIENT and AGENCY_ADMIN roles can be self-registered.
        SUPERADMIN and NURSE must be created via CLI or agency invitation flow.
        """
        if value == UserRole.SUPERADMIN:
            raise serializers.ValidationError(
                _('لا يمكن التسجيل كمدير نظام. يتم إنشاء مديري النظام عبر سطر الأوامر فقط.')
            )
        if value == UserRole.NURSE:
            raise serializers.ValidationError(
                _('لا يمكن التسجيل كممرض/ة. يتم إضافة الممرضين عبر دعوة الوكالة فقط.')
            )
        return value

    def validate_national_id(self, value: str) -> str:
        validate_egyptian_national_id(value)
        return value

    def validate_phone_number(self, value: str) -> str:
        validate_phone_number(value)
        return value

    def validate(self, attrs: dict) -> dict:
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': _('كلمتا المرور غير متطابقتين')
            })

        validate_password(password)

        return attrs

    def create(self, validated_data: dict) -> CustomUser:
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer with role as read-only.
    
    FR-007: role is read-only to prevent role changes via profile update.
    This is intentional for RBAC security - role changes require admin intervention.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'national_id',
            'phone_number',
            'email',
            'role',  # FR-007: Read-only to prevent privilege escalation
            'first_name_ar',
            'last_name_ar',
            'full_name',
            'is_active',
            'date_joined',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'national_id',
            'role',  # FR-007: Intentionally read-only
            'is_active',
            'date_joined',
            'updated_at'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'phone_number',
            'email',
            'first_name_ar',
            'last_name_ar'
        ]

    def validate_phone_number(self, value: str) -> str:
        validate_phone_number(value)

        user = self.instance
        if User.objects.filter(phone_number=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                _('هذا رقم الهاتف مسجل بالفعل')
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value: str) -> str:
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                _('كلمة المرور الحالية غير صحيحة')
            )
        return value

    def validate(self, attrs: dict) -> dict:
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': _('كلمتا المرور غير متطابقتين')
            })

        validate_password(new_password)

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        return user


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class KYCDocumentUploadSerializer(serializers.Serializer):
    """Validates KYC document upload requests."""

    document_type = serializers.ChoiceField(
        choices=[('NATIONAL_ID', 'National ID'), ('SYNDICATE_CARD', 'Syndicate Card')],
        help_text=_('نوع المستند: NATIONAL_ID أو SYNDICATE_CARD'),
    )
    document_file = serializers.FileField(
        help_text=_('صورة المستند (JPEG, PNG — حد أقصى 10 ميجابايت)'),
    )

    def validate_document_file(self, value):
        """Validate file type and size."""
        # Check file size (10MB max)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                _('حجم الملف أكبر من الحد المسموح (10 ميجابايت)')
            )

        # Check file extension
        allowed_extensions = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'}
        ext = value.name.rsplit('.', 1)[-1].lower() if '.' in value.name else ''
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                _('نوع الملف غير مدعوم. الأنواع المسموحة: JPEG, PNG, BMP, TIFF, WebP')
            )

        return value


class NurseDocumentSerializer(serializers.Serializer):
    """Read serializer for NurseDocument responses."""

    id = serializers.UUIDField(read_only=True)
    document_type = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    rejection_reason = serializers.CharField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    verified_at = serializers.DateTimeField(read_only=True)
