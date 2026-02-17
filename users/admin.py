from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, UserRole, PatientProfile, NurseProfile


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    
    list_display = (
        'national_id',
        'phone_number',
        'role',
        'is_active',
        'is_staff',
        'date_joined'
    )
    
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser'
    )
    
    search_fields = (
        'national_id',
        'phone_number',
        'email',
        'first_name_ar',
        'last_name_ar'
    )
    
    ordering = ('-date_joined',)
    
    readonly_fields = (
        'id',
        'date_joined',
        'updated_at'
    )
    
    fieldsets = (
        (_('معلومات الأساسية'), {
            'fields': (
                'id',
                'national_id',
                'password'
            )
        }),
        (_('معلومات الاتصال'), {
            'fields': (
                'phone_number',
                'email'
            )
        }),
        (_('معلومات شخصية'), {
            'fields': (
                'first_name_ar',
                'last_name_ar',
                'role'
            )
        }),
        (_('الصلاحيات'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('تواريخ مهمة'), {
            'fields': (
                'date_joined',
                'updated_at'
            )
        }),
    )
    
    add_fieldsets = (
        (_('إنشاء مستخدم جديد'), {
            'classes': ('wide',),
            'fields': (
                'national_id',
                'phone_number',
                'password1',
                'password2',
                'role',
                'is_active',
                'is_staff'
            )
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'wearables_enabled', 'created_at')
    list_filter = ('gender', 'wearables_enabled')
    search_fields = ('user__national_id', 'user__phone_number', 'emergency_contact')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'syndicate_number', 'rating', 'is_available', 'verification_status', 'created_at')
    list_filter = ('is_available', 'verification_status')
    search_fields = ('user__national_id', 'user__phone_number', 'syndicate_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)