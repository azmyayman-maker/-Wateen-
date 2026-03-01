from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

from .validators import validate_egyptian_national_id, validate_phone_number


class UserRole(models.TextChoices):
    PATIENT = "PATIENT", _("Patient")
    NURSE = "NURSE", _("Nurse")
    AGENCY_ADMIN = "AGENCY_ADMIN", _("Agency Admin")
    SUPERADMIN = "SUPERADMIN", _("Super Admin")


class CustomUserManager(BaseUserManager["CustomUser"]):
    def create_user(
        self,
        national_id: str,
        phone_number: str,
        password: str | None = None,
        **extra_fields,
    ) -> "CustomUser":
        if not national_id:
            raise ValueError(_("الرقم القومي مطلوب"))

        if not phone_number:
            raise ValueError(_("رقم الهاتف مطلوب"))

        validate_egyptian_national_id(national_id)
        validate_phone_number(phone_number)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(
            national_id=national_id, phone_number=phone_number, **extra_fields
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
        **extra_fields,
    ) -> "CustomUser":
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.SUPERADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(national_id, phone_number, password, **extra_fields)

    def get_by_natural_key(self, national_id: str) -> "CustomUser":
        return self.get(national_id=national_id)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
        help_text=_("معرّف فريد للمستخدم"),
    )

    national_id = models.CharField(
        _("الرقم القومي"),
        max_length=14,
        unique=True,
        db_index=True,
        validators=[validate_egyptian_national_id],
        help_text=_("الرقم القومي المصري - 14 رقم"),
    )

    phone_number = models.CharField(
        _("رقم الهاتف"),
        max_length=15,
        unique=True,
        validators=[validate_phone_number],
        help_text=_("رقم الهاتف المحمول - 11 رقم"),
    )

    email = models.EmailField(
        _("البريد الإلكتروني"),
        blank=True,
        null=True,
        help_text=_("البريد الإلكتروني (اختياري)"),
    )

    role = models.CharField(
        _("الدور"),
        max_length=15,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        help_text=_("دور المستخدم في النظام"),
    )

    # B2B2C: Link users (especially AGENCY_ADMIN) to their agency. 
    # The ticket specifies AgencyProfile maps 1:1 to a CustomUser with the role AGENCY_ADMIN.
    # However, since one agency could theoretically have multiple admins, we follow the ticket strictly:
    agency = models.OneToOneField(
        "AgencyProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_user",
        verbose_name=_("الشركة/الوكالة"),
        help_text=_("الشركة التابع لها المستخدم (للمديرين)"),
    )

    first_name_ar = models.CharField(
        _("الاسم الأول"), max_length=100, blank=True, default=""
    )

    last_name_ar = models.CharField(
        _("اسم العائلة"), max_length=100, blank=True, default=""
    )

    is_active = models.BooleanField(
        _("نشط"), default=True, help_text=_("تحديد ما إذا كان المستخدم نشطاً")
    )

    is_staff = models.BooleanField(
        _("موظف"),
        default=False,
        help_text=_("تحديد ما إذا كان المستخدم يمكنه الدخول لصفحة الإدارة"),
    )

    date_joined = models.DateTimeField(_("تاريخ التسجيل"), default=timezone.now)

    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "national_id"
    REQUIRED_FIELDS = ["phone_number"]

    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمون")
        db_table = "users_customuser"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.national_id

    def get_full_name(self) -> str:
        return f"{self.first_name_ar} {self.last_name_ar}".strip() or self.national_id

    def get_short_name(self) -> str:
        return self.first_name_ar or self.national_id

    @property
    def is_nurse(self) -> bool:
        return self.role == UserRole.NURSE

    @property
    def is_patient(self) -> bool:
        return self.role == UserRole.PATIENT

    @property
    def is_agency_admin(self) -> bool:
        return self.role == UserRole.AGENCY_ADMIN

    @property
    def is_superadmin(self) -> bool:
        return self.role == UserRole.SUPERADMIN

    @property
    def is_admin_user(self) -> bool:
        return self.role == UserRole.SUPERADMIN or self.is_superuser


class VerificationStatus(models.TextChoices):
    PENDING = "PENDING", _("قيد المراجعة")
    VERIFIED = "VERIFIED", _("موثق")
    REJECTED = "REJECTED", _("مرفوض")


class GenderChoices(models.TextChoices):
    MALE = "MALE", _("ذكر")
    FEMALE = "FEMALE", _("أنثى")


class AgencyStatus(models.TextChoices):
    PENDING = "pending", _("قيد المراجعة")
    VERIFIED = "verified", _("موثق")
    SUSPENDED = "suspended", _("موقوف")
    REJECTED = "rejected", _("مرفوض")


class DispatchMode(models.TextChoices):
    AUTO = "AUTO", _("آلي")
    MANUAL = "MANUAL", _("يدوي")


class AgencyProfile(models.Model):
    """
    B2B B2B2C Tenant Profile: Represents a verified agency.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
    )
    manager_name = models.CharField(
        _("اسم المدير"),
        max_length=255,
    )
    commercial_registry = models.CharField(
        _("السجل التجاري"),
        max_length=100,
        unique=True,
    )
    moh_license_number = models.CharField(
        _("رقم ترخيص وزارة الصحة"),
        max_length=100,
        unique=True,
    )
    tax_id = models.CharField(
        _("البطاقة الضريبية"),
        max_length=100,
        unique=True,
    )
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=AgencyStatus.choices,
        default=AgencyStatus.PENDING,
    )
    coverage_polygon = gis_models.PolygonField(
        _("نطاق التغطية"),
        srid=4326,
        null=True,
        blank=True,
    )
    rating = models.FloatField(
        _("التقييم"),
        default=0.0,
    )
    network_capacity = models.PositiveIntegerField(
        _("سعة الشبكة (عدد الممرضين)"),
        default=0,
    )
    dispatch_mode = models.CharField(
        _("آلية التوزيع"),
        max_length=10,
        choices=DispatchMode.choices,
        default=DispatchMode.MANUAL,
    )
    wallet_balance = models.DecimalField(
        _("رصيد المحفظة"),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    stripe_account_id = models.CharField(
        _("معرف حساب سترايب"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Stripe Connect Account ID for payouts"),
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("ملف الشركة/الوكالة")
        verbose_name_plural = _("ملفات الشركات/الوكالات")
        db_table = "users_agency_profile"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["rating"]),
            GistIndex(fields=["coverage_polygon"]),
        ]

    def __str__(self) -> str:
        return f"AgencyProfile({self.manager_name})"


class PatientProfile(models.Model):
    """Profile containing patient-specific medical and personal data."""

    user = models.OneToOneField(
        "users.CustomUser",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="patient_profile",
        verbose_name=_("المستخدم"),
    )
    date_of_birth = models.DateField(
        _("تاريخ الميلاد"),
        null=True,
        blank=True,
    )
    gender = models.CharField(
        _("الجنس"),
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        default="",
    )
    address_text = models.TextField(
        _("العنوان"),
        blank=True,
        default="",
    )
    home_location = gis_models.PointField(
        _("موقع المنزل"),
        geography=True,
        srid=4326,
        null=True,
        blank=True,
    )
    medical_notes = models.TextField(
        _("ملاحظات طبية"),
        blank=True,
        default="",
    )
    emergency_contact = models.CharField(
        _("رقم الطوارئ"),
        max_length=15,
        blank=True,
        default="",
    )
    wearables_enabled = models.BooleanField(
        _("أجهزة قابلة للارتداء"),
        default=False,
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("ملف المريض")
        verbose_name_plural = _("ملفات المرضى")
        db_table = "users_patient_profile"

    def __str__(self) -> str:
        return f"PatientProfile({self.user.national_id})"


class NurseProfile(models.Model):
    """Profile containing nurse-specific professional and verification data."""

    user = models.OneToOneField(
        "users.CustomUser",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="nurse_profile",
        verbose_name=_("المستخدم"),
    )
    agency = models.ForeignKey(
        "AgencyProfile",
        on_delete=models.CASCADE,
        related_name="nurses",
        verbose_name=_("الشركة/الوكالة التابع لها"),
        # Agency assignment is now fully strictly enforced at the database level.
    )
    national_id_document = models.CharField(
        _("رقم الهوية المهنية"),
        max_length=50,
        blank=True,
        default="",
    )
    syndicate_number = models.CharField(
        _("رقم النقابة"),
        max_length=50,
        blank=True,
        default="",
        unique=True,
    )
    syndicate_expiry = models.DateField(
        _("انتهاء عضوية النقابة"),
        null=True,
        blank=True,
    )
    specializations = models.JSONField(
        _("التخصصات"),
        default=list,
        blank=True,
    )
    rating = models.DecimalField(
        _("التقييم"),
        max_digits=3,
        decimal_places=2,
        default=5.00,
    )
    is_available = models.BooleanField(
        _("متاح"),
        default=False,
    )
    last_location = gis_models.PointField(
        _("آخر موقع"),
        geography=True,
        srid=4326,
        null=True,
        blank=True,
    )
    verification_status = models.CharField(
        _("حالة التحقق"),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("ملف الممرض/ة")
        verbose_name_plural = _("ملفات الممرضين")
        db_table = "users_nurse_profile"
        # constraints = [
        #     CheckConstraint(
        #         check=~Q(agency__isnull=True),
        #         name='nurse_must_belong_to_agency'
        #     ),
        # ]
        indexes = [
            GistIndex(fields=["last_location"]),
        ]

    def __str__(self) -> str:
        return f"NurseProfile({self.user.national_id})"

    def clean(self):
        """
        Validate that the nurse is assigned to an agency.

        B2B2C Rule: Nurses must belong to an agency - they are not freelancers.
        This enforces the business rule at model validation level.
        """
        super().clean()
        if not self.agency_id:
            raise ValidationError(
                {"agency": _("الممرض/ة يجب أن تكون تابعة للوكالة.")}
            )

    def save(self, *args, **kwargs):
        """Override save to run full validation including clean()."""
        skip_full_clean = kwargs.pop("skip_full_clean", False)
        if not skip_full_clean:
            self.full_clean()
        super().save(*args, **kwargs)

class InvitationStatus(models.TextChoices):
    PENDING = "PENDING", _("قيد الانتظار")
    ACCEPTED = "ACCEPTED", _("مقبول")
    EXPIRED = "EXPIRED", _("منتهي الصلاحية")


class NurseInvitation(models.Model):
    """
    Cryptographic Nurse Invitation Model.
    Binds a nurse to a specific agency securely prior to the nurse registering an account.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(
        "AgencyProfile",
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name=_("الوكالة"),
    )
    phone = models.CharField(_("الهاتف"), max_length=20)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(
        _("الحالة"),
        max_length=15,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
    )
    expires_at = models.DateTimeField(_("تاريخ الانتهاء"))
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        verbose_name = _("دعوة ممرض/ة")
        verbose_name_plural = _("دعوات الممرضين")
        db_table = "users_nurse_invitation"
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Invite({self.phone}) -> {self.agency.manager_name}"

    @property
    def is_valid(self) -> bool:
        return self.status == InvitationStatus.PENDING and self.expires_at > timezone.now()


class DocumentType(models.TextChoices):
    NATIONAL_ID = "NATIONAL_ID", _("بطاقة الرقم القومي")
    SYNDICATE_CARD = "SYNDICATE_CARD", _("كارنيه النقابة")


class DocumentStatus(models.TextChoices):
    PENDING = "PENDING", _("قيد المراجعة")
    VERIFIED = "VERIFIED", _("تم التحقق")
    REJECTED = "REJECTED", _("مرفوض")


def kyc_document_upload_path(instance, filename):
    """Generate upload path: kyc_documents/<nurse_uuid>/<document_type>/<filename>"""
    return f"kyc_documents/{instance.nurse.user_id}/{instance.document_type}/{filename}"


class NurseDocument(models.Model):
    """Stores uploaded KYC documents for nurse verification (National ID, Syndicate Card)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرّف"),
    )
    nurse = models.ForeignKey(
        "users.NurseProfile",
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("الممرض/ة"),
    )
    document_type = models.CharField(
        _("نوع المستند"),
        max_length=20,
        choices=DocumentType.choices,
    )
    document_file = models.FileField(
        _("ملف المستند"),
        upload_to=kyc_document_upload_path,
    )
    ocr_data = models.JSONField(
        _("بيانات OCR"),
        default=dict,
        blank=True,
        help_text=_("البيانات المستخرجة من المستند عبر OCR"),
    )
    extracted_national_id = models.CharField(
        _("الرقم القومي المستخرج"),
        max_length=14,
        blank=True,
        default="",
        help_text=_("الرقم القومي المكوّن من 14 رقم المستخرج من الصورة"),
    )
    status = models.CharField(
        _("الحالة"),
        max_length=10,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING,
    )
    rejection_reason = models.TextField(
        _("سبب الرفض"),
        blank=True,
        default="",
    )
    uploaded_at = models.DateTimeField(
        _("تاريخ الرفع"),
        auto_now_add=True,
    )
    verified_at = models.DateTimeField(
        _("تاريخ التحقق"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("مستند الممرض/ة")
        verbose_name_plural = _("مستندات الممرضين")
        db_table = "users_nurse_document"
        ordering = ["-uploaded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["nurse", "document_type"],
                name="unique_nurse_document_type",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_document_type_display()} — {self.nurse}"
