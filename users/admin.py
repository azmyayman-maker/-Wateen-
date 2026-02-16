from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, UserRole


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