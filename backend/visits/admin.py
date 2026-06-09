from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    DispatchOffer,
    EstimateLog,
    PricingFactor,
    ServiceType,
    Transaction,
    Visit,
)


class DispatchOfferInline(admin.TabularInline):
    model = DispatchOffer
    extra = 0
    readonly_fields = ("nurse", "status", "expires_at", "responded_at", "offered_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "agency",
        "nurse",
        "status",
        "service_type",
        "created_at",
    )
    list_filter = ("status", "service_type", "agency")
    search_fields = ("patient__user__national_id", "nurse__user__national_id")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "routed_at",
        "reroute_attempts",
        "base_price",
        "time_multiplier",
        "distance_km",
        "distance_rate",
        "ai_surge_coefficient",
        "final_price",
    )
    raw_id_fields = ("patient", "nurse", "agency")
    inlines = [DispatchOfferInline]
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "patient",
                    "agency",
                    "nurse",
                    "status",
                    "service_type",
                    "location",
                )
            },
        ),
        (
            _("Pricing"),
            {
                "fields": (
                    "base_price",
                    "distance_fee",
                    "distance_km",
                    "distance_rate",
                    "time_multiplier",
                    "ai_surge_coefficient",
                    "final_price",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "routed_at", "reroute_attempts", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


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


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "visit",
        "agency",
        "amount_paid",
        "wateen_take_rate",
        "agency_payout",
        "status",
        "created_at",
    )
    list_filter = ("status", "agency")
    search_fields = ("visit__id", "agency__manager_name")
    readonly_fields = (
        "id",
        "amount_paid",
        "wateen_take_rate",
        "agency_payout",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("visit", "agency", "status")}),
        (
            _("Financial"),
            {"fields": ("amount_paid", "wateen_take_rate", "agency_payout")},
        ),
        (
            _("Paymob"),
            {"fields": ("paymob_order_id", "paymob_transaction_id")},
        ),
        (
            _("Settlement"),
            {"fields": ("settled_at",)},
        ),
        (
            _("Metadata"),
            {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
