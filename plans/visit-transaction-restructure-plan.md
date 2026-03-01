# Implementation Plan: Visit & Transaction Model Restructuring (P1-T4)

## Overview

This plan details the changes needed to implement the Visit and Transaction models according to the specification in `specs/010-visit-transaction-restructure/spec.md`.

---

## Task 1: Update Visit Model (`visits/models.py`)

### 1.1 Change ForeignKeys to PROTECT

**Current:**

```python
agency = models.ForeignKey(
    "users.AgencyProfile",
    on_delete=models.SET_NULL,  # Line 151-157
    ...
)
nurse = models.ForeignKey(
    "users.NurseProfile",
    on_delete=models.SET_NULL,  # Line 159-165
    ...
)
```

**Change to:**

```python
agency = models.ForeignKey(
    "users.AgencyProfile",
    on_delete=models.PROTECT,  # Prevent deletion if visits exist
    related_name="visits",
    verbose_name=_("الشركة/الوكالة المنفذة"),
    null=True,
    blank=True,
)
nurse = models.ForeignKey(
    "users.NurseProfile",
    on_delete=models.PROTECT,  # Prevent deletion if visits exist
    null=True,
    blank=True,
    related_name="visits",
    verbose_name=_("الممرض/ة"),
)
```

### 1.2 Add Missing Pricing Fields

Add after `ai_surge_coefficient` field (around line 219):

```python
distance_km = models.DecimalField(
    _("المسافة بالكيلومتر"),
    max_digits=6,
    decimal_places=2,
    null=True,
    blank=True,
    help_text=_("المسافة من الوكالة إلى موقع المريض"),
)
distance_rate = models.DecimalField(
    _("سعر الكيلومتر"),
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True,
    help_text=_("سعر لكل كيلومتر"),
)
```

### 1.3 Implement Immutable Pricing Snapshot

Add to `Visit` model (before `__str__` method, around line 248):

```python
def save(self, *args, **kwargs):
    """Override save to enforce immutable pricing snapshot."""
    if self.pk:
        # This is an update - check if pricing fields changed
        try:
            old_visit = Visit.objects.get(pk=self.pk)
            pricing_fields = ['base_price', 'time_multiplier', 'distance_km',
                            'distance_rate', 'ai_surge_coefficient', 'final_price']
            for field_name in pricing_fields:
                old_value = getattr(old_visit, field_name)
                new_value = getattr(self, field_name)
                if old_value != new_value:
                    raise ValidationError(
                        _("لا يمكن تعديل سعر الزيارة بعد الإنشاء. السعر النهائي هو: %(price)s"),
                        code="immutable_pricing",
                        params={"price": old_visit.final_price}
                    )
        except Visit.DoesNotExist:
            pass

    super().save(*args, **kwargs)
```

---

## Task 2: Restructure Transaction Model (`visits/models.py`)

### 2.1 Update Field Names and Add Missing Fields

Replace the existing Transaction model (lines 336-427) with:

```python
class TransactionStatus(models.TextChoices):
    ESCROWED = "ESCROWED", _("في الضمان")
    SETTLED = "SETTLED", _("تمت التسوية")
    REFUNDED = "REFUNDED", _("تم الاسترجاع")


class Transaction(models.Model):
    """
    Represents a financial transaction associated with a visit.
    Handles the split between the platform (Wateen take rate) and the agency.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
    )
    visit = models.OneToOneField(
        Visit,
        on_delete=models.PROTECT,
        related_name="transaction",
        verbose_name=_("الزيارة"),
    )
    agency = models.ForeignKey(
        "users.AgencyProfile",
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name=_("الوكالة"),
    )
    amount_paid = models.DecimalField(
        _("المبلغ المدفوع"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("المبلغ الإجمالي المدفوع من المريض"),
    )
    wateen_take_rate = models.DecimalField(
        _("نسبة المنصة"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("15.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
        help_text=_("نسبة حصة المنصة (افتراضي 15%)"),
    )
    agency_payout = models.DecimalField(
        _("مبلغ الوكالة"),
        max_digits=10,
        decimal_places=2,
        editable=False,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("مبلغ الوكالة بعد خصم حصة المنصة"),
    )
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.ESCROWED,
    )
    paymob_order_id = models.CharField(
        _("معرف الطلب في باي موب"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Paymob Order ID"),
    )
    paymob_transaction_id = models.Column(
        models.CharField(
            _("معرف المعاملة في باي موب"),
            max_length=255,
            null=True,
            blank=True,
            help_text=_("Paymob Transaction ID بعد الدفع الناجح"),
        )
    )
    settled_at = models.DateTimeField(
        _("تاريخ التسوية"),
        null=True,
        blank=True,
        help_text=_("تاريخ تحويل المبلغ للوكالة"),
    )
    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("تاريخ التحديث"),
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        """Auto-calculate agency_payout before saving."""
        if self.amount_paid is not None:
            # Calculate agency payout: amount_paid * 0.85
            self.agency_payout = self.amount_paid * Decimal('0.85')

        # Set settled_at when status changes to SETTLED
        if self.status == TransactionStatus.SETTLED and not self.settled_at:
            from django.utils import timezone
            self.settled_at = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("عملية مالية")
        verbose_name_plural = _("العمليات المالية")
        db_table = "visits_transaction"

    def __str__(self) -> str:
        return f"Transaction({str(self.id)[:8]}) - {self.status}"
```

---

## Task 3: Update visits/admin.py

### 3.1 Update VisitAdmin

Replace the existing VisitAdmin with:

```python
@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "agency", "nurse", "status", "final_price", "created_at")
    list_filter = ("status", "agency", "service_type")
    search_fields = ("patient__user__national_id", "nurse__user__national_id")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        # Financial fields - read-only for tamper proofing
        "base_price",
        "time_multiplier",
        "distance_km",
        "distance_rate",
        "ai_surge_coefficient",
        "final_price",
    )
    raw_id_fields = ("patient", "nurse", "agency")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("patient", "agency", "nurse", "status", "location", "service_type")
        }),
        (_("التسعير"), {
            "fields": ("base_price", "time_multiplier", "distance_km",
                      "distance_rate", "ai_surge_coefficient", "final_price"),
            "classes": ("collapse",),
        }),
        (_("Metadata"), {
            "fields": ("id", "reroute_attempts", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
```

### 3.2 Register TransactionAdmin

Add after VisitAdmin:

```python
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "visit", "agency", "amount_paid", "wateen_take_rate",
                   "agency_payout", "status", "settled_at")
    list_filter = ("status", "agency")
    search_fields = ("visit__id", "agency__manager_name", "paymob_order_id")
    readonly_fields = (
        "id",
        "amount_paid",
        "wateen_take_rate",
        "agency_payout",  # Calculated automatically, not editable
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("visit", "agency")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("visit", "agency", "status")
        }),
        (_("المالية"), {
            "fields": ("amount_paid", "wateen_take_rate", "agency_payout"),
        }),
        (_("باي موب"), {
            "fields": ("paymob_order_id", "paymob_transaction_id"),
            "classes": ("collapse",),
        }),
        (_("التسوية"), {
            "fields": ("settled_at", "created_at", "updated_at"),
        }),
    )
```

---

## Task 4: Update users/admin.py

### 4.1 Add GISModelAdmin for AgencyProfile

Add import at top:

```python
from django.contrib.gis.admin import GISModelAdmin
```

Add after existing admin registrations:

```python
@admin.register(AgencyProfile)
class AgencyProfileAdmin(GISModelAdmin):
    """Admin with interactive map widget for coverage_polygon."""

    list_display = ("manager_name", "commercial_registry", "status", "rating", "network_capacity")
    list_filter = ("status", "dispatch_mode")
    search_fields = ("manager_name", "commercial_registry", "tax_id")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    # GIS Model Admin settings
    default_lon = 30.8025  # Egypt center longitude
    default_lat = 26.8206   # Egypt center latitude
    default_zoom = 6

    fieldsets = (
        (None, {
            "fields": ("manager_name", "commercial_registry", "moh_license_number",
                      "tax_id", "status")
        }),
        (_("التغطية الجغرافية"), {
            "fields": ("coverage_polygon",),
            "description": _("ارسم نطاق التغطية على الخريطة"),
        }),
        (_("الأداء"), {
            "fields": ("rating", "network_capacity", "dispatch_mode", "wallet_balance"),
        }),
        (_("الدفع"), {
            "fields": ("stripe_account_id",),
            "classes": ("collapse",),
        }),
        (_("Metadata"), {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
```

---

## Important Notes

1. **Migration Required**: After implementing these changes, run:

   ```bash
   python manage.py makemigrations visits
   python manage.py migrate
   ```

2. **Data Migration**: The field renaming (stripe_payment_intent_id → paymob_order_id, etc.) will require a data migration to preserve existing data.

3. **Decimal Precision**: All financial calculations use `Decimal` from the Python standard library - never use `float` for money.

4. **Immutability**: The pricing snapshot is enforced at the application layer in `Visit.save()`. If a pricing field is changed after creation, `ValidationError` is raised.

5. **Paymob Integration**: The Transaction model now supports Paymob Order/Transaction IDs instead of Stripe.

---

## Files to Modify

| File               | Changes                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------ |
| `visits/models.py` | Update Visit FKs, add pricing fields, implement immutable pricing, restructure Transaction |
| `visits/admin.py`  | Update VisitAdmin with readonly fields/filters, add TransactionAdmin                       |
| `users/admin.py`   | Add AgencyProfileAdmin with GISModelAdmin                                                  |
