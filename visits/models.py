import uuid
from decimal import Decimal

from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceType(models.Model):
    """Represents a category of service with base pricing."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
    )
    name = models.CharField(
        _("اسم الخدمة"),
        max_length=100,
        unique=True,
        help_text=_("اسم الخدمة (مثال: تمريض منزلي، علاج طبيعي)"),
    )
    base_price = models.DecimalField(
        _("السعر الأساسي"),
        max_digits=10,
        decimal_places=2,
        help_text=_("السعر الأساسي بالجنيه المصري"),
    )
    surge_multiplier = models.DecimalField(
        _("معامل الزيادة"),
        max_digits=4,
        decimal_places=2,
        default=Decimal("1.0"),
        help_text=_("معامل زيادة السعر (الافتراضي 1.0)"),
    )
    description = models.TextField(
        _("الوصف"),
        blank=True,
        default="",
        help_text=_("وصف الخدمة"),
    )
    is_active = models.BooleanField(
        _("نشط"),
        default=True,
        help_text=_("هل الخدمة متاحة للحجز"),
    )
    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("تاريخ التحديث"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("نوع الخدمة")
        verbose_name_plural = _("أنواع الخدمات")
        db_table = "visits_service_type"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.base_price} EGP)"


class PricingFactor(models.Model):
    """Configurable pricing variable that drives price calculations."""

    key = models.CharField(
        _("المفتاح"),
        max_length=50,
        primary_key=True,
        help_text=_("معرف فريد للمتغير (مثال: per_km_rate)"),
    )
    value = models.DecimalField(
        _("القيمة"),
        max_digits=10,
        decimal_places=4,
        help_text=_("قيمة المتغير"),
    )
    description = models.CharField(
        _("الوصف"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("وصف للمتغير"),
    )
    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("تاريخ التحديث"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("عامل التسعير")
        verbose_name_plural = _("عوامل التسعير")
        db_table = "visits_pricing_factor"
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key}={self.value}"


class VisitStatus(models.TextChoices):
    PENDING_AGENCY = "pending_agency", _("في انتظار الوكالة")
    PENDING_NURSE = "pending_nurse", _("في انتظار الممرض")
    ACCEPTED = "accepted", _("مقبولة")
    EN_ROUTE = "en_route", _("في الطريق")
    IN_PROGRESS = "in_progress", _("جارية")
    COMPLETED = "completed", _("مكتملة")
    CANCELLED = "cancelled", _("ملغاة")


# Explicit allowed transitions map — the single source of truth for the state machine.
ALLOWED_TRANSITIONS = {
    VisitStatus.PENDING_AGENCY: [
        VisitStatus.PENDING_NURSE,
        VisitStatus.ACCEPTED,
        VisitStatus.CANCELLED,
    ],
    VisitStatus.PENDING_NURSE: [VisitStatus.ACCEPTED, VisitStatus.CANCELLED],
    VisitStatus.ACCEPTED: [VisitStatus.EN_ROUTE, VisitStatus.CANCELLED],
    VisitStatus.EN_ROUTE: [VisitStatus.IN_PROGRESS, VisitStatus.CANCELLED],
    VisitStatus.IN_PROGRESS: [VisitStatus.COMPLETED, VisitStatus.CANCELLED],
    VisitStatus.COMPLETED: [],  # Terminal state
    VisitStatus.CANCELLED: [],  # Terminal state
}


class Visit(models.Model):
    """Represents a single home-nursing visit request and its lifecycle."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
    )
    patient = models.ForeignKey(
        "users.PatientProfile",
        on_delete=models.CASCADE,
        related_name="visits",
        verbose_name=_("المريض"),
    )
    agency = models.ForeignKey(
        "users.AgencyProfile",
        on_delete=models.SET_NULL,
        related_name="visits",
        verbose_name=_("الشركة/الوكالة المنفذة"),
        null=True,  # Allow null temporarily for initial migration of existing P2P visits
        blank=True,
    )
    nurse = models.ForeignKey(
        "users.NurseProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
        verbose_name=_("الممرض/ة"),
    )
    status = models.CharField(
        _("الحالة"),
        max_length=15,
        choices=VisitStatus.choices,
        default=VisitStatus.PENDING_AGENCY,
        db_index=True,
    )
    location = gis_models.PointField(
        _("موقع الزيارة"),
        geography=True,
        srid=4326,
        help_text=_("الموقع الجغرافي للمريض عند طلب الزيارة"),
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
        verbose_name=_("نوع الخدمة"),
        help_text=_("نوع الخدمة التمريضية المطلوبة"),
    )
    base_price = models.DecimalField(
        _("السعر الأساسي"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("السعر الأساسي للخدمة"),
    )
    distance_fee = models.DecimalField(
        _("رسوم المسافة"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("رسوم المسافة المحسوبة"),
    )
    time_multiplier = models.DecimalField(
        _("معامل الوقت"),
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("معامل الوقت (ليلي/نهاري)"),
    )
    ai_surge_coefficient = models.DecimalField(
        _("معامل الذكاء الاصطناعي"),
        max_digits=4,
        decimal_places=2,
        default=Decimal("1.0"),
        help_text=_("معامل زيادة السعر (للاستخدام المستقبلية مع ML)"),
    )
    final_price = models.DecimalField(
        _("السعر النهائي"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("السعر النهائي المحسوب"),
    )
    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("تاريخ التحديث"),
        auto_now=True,
    )
    reroute_attempts = models.PositiveIntegerField(
        _("محاولات إعادة التوجيه"),
        default=0,
        help_text=_("عدد محاولات إعادة توجيه الزيارة إلى وكالات أخرى"),
    )

    class Meta:
        verbose_name = _("زيارة")
        verbose_name_plural = _("الزيارات")
        db_table = "visits_visit"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Visit({str(self.id)[:8]}—{self.status})"

    def transition_to(self, new_status: str) -> None:
        """
        Transition the visit to a new status.

        Validates the transition against the ALLOWED_TRANSITIONS map.
        Raises ValidationError if the transition is not allowed.
        Saves the model after a successful transition.
        """
        if new_status not in VisitStatus.values:
            raise ValidationError(
                _('الحالة "%(status)s" غير صالحة.'),
                code="invalid_status",
                params={"status": new_status},
            )

        allowed = ALLOWED_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValidationError(
                _('لا يمكن الانتقال من "%(current)s" إلى "%(new)s".'),
                code="invalid_transition",
                params={"current": self.status, "new": new_status},
            )

        self.status = new_status
        self.save(update_fields=["status", "updated_at"])


class EstimateLog(models.Model):
    """T038: Captures estimate request data for ML training."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
    )
    request_time = models.DateTimeField(
        _("وقت الطلب"),
        db_index=True,
        help_text=_("وقت طلب التسعير"),
    )
    location = gis_models.PointField(
        _("موقع العميل"),
        geography=True,
        srid=4326,
        help_text=_("موقع العميل عند طلب التسعير"),
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estimate_logs",
        verbose_name=_("نوع الخدمة"),
        help_text=_("نوع الخدمة المطلوبة"),
    )
    price_components = models.JSONField(
        _("مكونات السعر"),
        help_text=_("تفاصيل حساب السعر للتدريب على ML"),
    )
    ip_address = models.GenericIPAddressField(
        _("عنوان IP"),
        null=True,
        blank=True,
        help_text=_("عنوان IP للعميل"),
    )
    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("سجل التسعير")
        verbose_name_plural = _("سجلات التسعير")
        db_table = "visits_estimate_log"
        ordering = ["-request_time"]
        indexes = [
            models.Index(fields=["request_time"]),
            models.Index(fields=["service_type"]),
        ]

    def __str__(self) -> str:
        return f"EstimateLog({str(self.id)[:8]}—{self.request_time})"


class TransactionStatus(models.TextChoices):
    PENDING = "PENDING", _("قيد المعالجة")
    ESCROWED = "ESCROWED", _("في الضمان")
    SETTLED = "SETTLED", _("تمت التسوية")
    REFUNDED = "REFUNDED", _("تم الاسترجاع")
    FAILED = "FAILED", _("فشلت")


class Transaction(models.Model):
    """
    T027: Represents a financial transaction associated with a visit.
    Handles the split between the platform (take rate) and the agency.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    visit = models.OneToOneField(
        Visit,
        on_delete=models.CASCADE,
        related_name="transaction",
        verbose_name=_("الزيارة"),
    )
    stripe_payment_intent_id = models.CharField(
        _("معرف الدفع في سترايب"),
        max_length=255,
        blank=True,
        null=True,
    )
    total_amount = models.DecimalField(
        _("إجمالي المبلغ"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    take_rate_percent = models.DecimalField(
        _("نسبة المنصة"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("15.00"),  # Default 15%
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
    )
    take_rate_amount = models.DecimalField(
        _("مبلغ المنصة"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    agency_amount = models.DecimalField(
        _("مبلغ الوكالة"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.total_amount is not None and self.take_rate_percent is not None:
            expected_take_rate = (self.total_amount * self.take_rate_percent) / Decimal("100")
            if self.take_rate_amount is not None and self.take_rate_amount != expected_take_rate:
                raise ValidationError({"take_rate_amount": _("مبلغ المنصة يجب أن يساوي إجمالي المبلغ مضروباً في نسبة المنصة مقسومة على 100.")})
            if self.take_rate_amount is not None and self.agency_amount is not None:
                expected_agency_amount = self.total_amount - self.take_rate_amount
                if self.agency_amount != expected_agency_amount:
                    raise ValidationError({"agency_amount": _("مبلغ الوكالة يجب أن يساوي إجمالي المبلغ ناقص مبلغ المنصة.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("عملية مالية")
        verbose_name_plural = _("العمليات المالية")
        db_table = "visits_transaction"

    def __str__(self):
        return f"Transaction({self.id}) - {self.status}"

    def calculate_split(self):
        """Calculates the split between platform and agency."""
        self.take_rate_amount = (self.total_amount * self.take_rate_percent) / 100
        self.agency_amount = self.total_amount - self.take_rate_amount
