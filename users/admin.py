from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.gis.admin import GISModelAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import (
    AgencyProfile,
    CustomUser,
    NurseDocument,
    NurseProfile,
    PatientProfile,
    KYCDocument,
    KYCAuditLog,
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    list_display = (
        "national_id",
        "phone_number",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = ("role", "is_active", "is_staff", "is_superuser")

    search_fields = (
        "national_id",
        "phone_number",
        "email",
        "first_name_ar",
        "last_name_ar",
    )

    ordering = ("-date_joined",)

    readonly_fields = ("id", "date_joined", "updated_at")

    fieldsets = (
        (_("معلومات الأساسية"), {"fields": ("id", "national_id", "password")}),
        (_("معلومات الاتصال"), {"fields": ("phone_number", "email")}),
        (_("معلومات شخصية"), {"fields": ("first_name_ar", "last_name_ar", "role")}),
        (
            _("الصلاحيات"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("تواريخ مهمة"), {"fields": ("date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (
            _("إنشاء مستخدم جديد"),
            {
                "classes": ("wide",),
                "fields": (
                    "national_id",
                    "phone_number",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date_of_birth",
        "gender",
        "wearables_enabled",
        "created_at",
    )
    list_filter = ("gender", "wearables_enabled")
    search_fields = ("user__national_id", "user__phone_number", "emergency_contact")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "syndicate_number",
        "rating",
        "is_available",
        "verification_status",
        "created_at",
    )
    list_filter = ("is_available", "verification_status")
    search_fields = ("user__national_id", "user__phone_number", "syndicate_number")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)


@admin.register(NurseDocument)
class NurseDocumentAdmin(admin.ModelAdmin):
    list_display = ("nurse", "document_type", "status", "uploaded_at", "verified_at")
    list_filter = ("status", "document_type")
    search_fields = ("nurse__user__national_id", "nurse__user__phone_number")
    readonly_fields = (
        "id",
        "ocr_data",
        "extracted_national_id",
        "uploaded_at",
        "verified_at",
    )
    raw_id_fields = ("nurse",)


@admin.register(AgencyProfile)
class AgencyProfileAdmin(GISModelAdmin):
    list_display = (
        "manager_name",
        "commercial_registry",
        "status",
        "rating",
        "network_capacity",
        "dispatch_mode",
        "wallet_balance",
    )
    list_filter = ("status", "dispatch_mode")
    search_fields = ("manager_name", "commercial_registry", "moh_license_number")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "manager_name",
                    "commercial_registry",
                    "moh_license_number",
                    "tax_id",
                    "status",
                )
            },
        ),
        (
            _("Geographic Coverage"),
            {"fields": ("coverage_polygon",)},
        ),
        (
            _("Network"),
            {
                "fields": (
                    "rating",
                    "network_capacity",
                    "dispatch_mode",
                    "wallet_balance",
                )
            },
        ),
        (
            _("Metadata"),
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    default_lon = 30.8025
    default_lat = 26.8206
    default_zoom = 6


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for Agency KYC documents.
    Provides easy oversight of pending applications and historical versions.
    """
    list_display = (
        "agency", 
        "document_type", 
        "status", 
        "version", 
        "uploaded_at"
    )
    list_filter = ("status", "document_type", "uploaded_at")
    search_fields = (
        "agency__manager_name", 
        "agency__commercial_registry", 
        "agency__tax_id"
    )
    readonly_fields = ("id", "version", "uploaded_at")
    raw_id_fields = ("agency",)
    
    fieldsets = (
        (None, {
            "fields": ("agency", "document_type", "status", "version")
        }),
        (_("Review Details"), {
            "fields": ("reviewer_notes",)
        }),
        (_("File & Metadata"), {
            "fields": ("file", "id", "uploaded_at")
        }),
    )


@admin.register(KYCAuditLog)
class KYCAuditLogAdmin(admin.ModelAdmin):
    """
    Immutable audit log interface. All fields are read-only.
    """
    list_display = ("agency", "action", "reviewer", "ip_address", "timestamp")
    list_filter = ("action", "timestamp", "reviewer")
    search_fields = ("agency__manager_name", "notes", "ip_address")
    readonly_fields = ("id", "agency", "reviewer", "action", "notes", "ip_address", "user_agent", "timestamp")
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
        
    def has_change_permission(self, request: HttpRequest, obj: KYCAuditLog | None = None) -> bool:
        return False
        
    def has_delete_permission(self, request: HttpRequest, obj: KYCAuditLog | None = None) -> bool:
        return False

