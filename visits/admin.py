from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import EstimateLog, PricingFactor, ServiceType, Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "nurse", "status", "service_type", "created_at")
    list_filter = ("status", "service_type")
    search_fields = ("patient__user__national_id", "nurse__user__national_id")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("patient", "nurse")
    ordering = ("-created_at",)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    """T030/T032: Admin for ServiceType model."""

    list_display = ("name", "base_price", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)

    fieldsets = (
        (None, {"fields": ("name", "base_price", "description", "is_active")}),
        (
            _("Metadata"),
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(PricingFactor)
class PricingFactorAdmin(admin.ModelAdmin):
    """T031/T033: Admin for PricingFactor model."""

    list_display = ("key", "value", "description", "updated_at")
    search_fields = ("key", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("key",)

    fieldsets = (
        (None, {"fields": ("key", "value", "description")}),
        (
            _("Metadata"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(EstimateLog)
class EstimateLogAdmin(admin.ModelAdmin):
    """T042: Read-only admin for EstimateLog model."""

    list_display = ("id", "service_type", "request_time", "ip_address", "created_at")
    list_filter = ("service_type", "request_time")
    search_fields = ("service_type__name", "ip_address")
    readonly_fields = (
        "id",
        "request_time",
        "location",
        "service_type",
        "price_components",
        "ip_address",
        "created_at",
    )
    ordering = ("-request_time",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
