from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

from .validators import validate_egyptian_national_id, validate_phone_number


class UserRole(models.TextChoices):
    PATIENT = 'PATIENT', _('Patient')
    NURSE = 'NURSE', _('Nurse')
    DOCTOR = 'DOCTOR', _('Doctor')
    ADMIN = 'ADMIN', _('Admin')


class CustomUserManager(BaseUserManager['CustomUser']):
    def create_user(
        self,
        national_id: str,
        phone_number: str,
        password: str | None = None,
        **extra_fields
    ) -> 'CustomUser':
        if not national_id:
            raise ValueError(_('الرقم القومي مطلوب'))
        
        if not phone_number:
            raise ValueError(_('رقم الهاتف مطلوب'))
        
        validate_egyptian_national_id(national_id)
        validate_phone_number(phone_number)
        
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(
            national_id=national_id,
            phone_number=phone_number,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_superuser(
        self,
        national_id: str,
        phone_number: str,
        password: str | None = None,
        **extra_fields
    ) -> 'CustomUser':
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(national_id, phone_number, password, **extra_fields)
    
    def get_by_natural_key(self, national_id: str) -> 'CustomUser':
        return self.get(national_id=national_id)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('المعرّف'),
        help_text=_('معرّف فريد للمستخدم')
    )
    
    national_id = models.CharField(
        _('الرقم القومي'),
        max_length=14,
        unique=True,
        db_index=True,
        validators=[validate_egyptian_national_id],
        help_text=_('الرقم القومي المصري - 14 رقم')
    )
    
    phone_number = models.CharField(
        _('رقم الهاتف'),
        max_length=15,
        unique=True,
        validators=[validate_phone_number],
        help_text=_('رقم الهاتف المحمول - 11 رقم')
    )
    
    email = models.EmailField(
        _('البريد الإلكتروني'),
        blank=True,
        null=True,
        help_text=_('البريد الإلكتروني (اختياري)')
    )
    
    role = models.CharField(
        _('الدور'),
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        help_text=_('دور المستخدم في النظام')
    )
    
    first_name_ar = models.CharField(
        _('الاسم الأول'),
        max_length=100,
        blank=True,
        default=''
    )
    
    last_name_ar = models.CharField(
        _('اسم العائلة'),
        max_length=100,
        blank=True,
        default=''
    )
    
    is_active = models.BooleanField(
        _('نشط'),
        default=True,
        help_text=_('تحديد ما إذا كان المستخدم نشطاً')
    )
    
    is_staff = models.BooleanField(
        _('موظف'),
        default=False,
        help_text=_('تحديد ما إذا كان المستخدم يمكنه الدخول لصفحة الإدارة')
    )
    
    date_joined = models.DateTimeField(
        _('تاريخ التسجيل'),
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True
    )
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'national_id'
    REQUIRED_FIELDS = ['phone_number']
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        db_table = 'users_customuser'
        ordering = ['-date_joined']
    
    def __str__(self) -> str:
        return self.national_id
    
    def get_full_name(self) -> str:
        return f'{self.first_name_ar} {self.last_name_ar}'.strip() or self.national_id
    
    def get_short_name(self) -> str:
        return self.first_name_ar or self.national_id
    
    @property
    def is_doctor(self) -> bool:
        return self.role == UserRole.DOCTOR
    
    @property
    def is_nurse(self) -> bool:
        return self.role == UserRole.NURSE
    
    @property
    def is_patient(self) -> bool:
        return self.role == UserRole.PATIENT
    
    @property
    def is_admin_user(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_superuser