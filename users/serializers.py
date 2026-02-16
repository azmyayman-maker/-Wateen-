from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser, UserRole
from .validators import validate_egyptian_national_id, validate_phone_number


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
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
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'national_id',
            'phone_number',
            'email',
            'role',
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
            'role',
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