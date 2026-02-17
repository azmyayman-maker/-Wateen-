import uuid

from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class VisitStatus(models.TextChoices):
    PENDING = 'PENDING', _('قيد الانتظار')
    MATCHED = 'MATCHED', _('تم المطابقة')
    ACCEPTED = 'ACCEPTED', _('مقبولة')
    ON_WAY = 'ON_WAY', _('في الطريق')
    ARRIVED = 'ARRIVED', _('وصل')
    IN_PROGRESS = 'IN_PROGRESS', _('جارية')
    COMPLETED = 'COMPLETED', _('مكتملة')
    CANCELLED = 'CANCELLED', _('ملغاة')


# Explicit allowed transitions map — the single source of truth for the state machine.
ALLOWED_TRANSITIONS = {
    VisitStatus.PENDING: [VisitStatus.MATCHED, VisitStatus.CANCELLED],
    VisitStatus.MATCHED: [VisitStatus.ACCEPTED, VisitStatus.CANCELLED],
    VisitStatus.ACCEPTED: [VisitStatus.ON_WAY, VisitStatus.CANCELLED],
    VisitStatus.ON_WAY: [VisitStatus.ARRIVED, VisitStatus.CANCELLED],
    VisitStatus.ARRIVED: [VisitStatus.IN_PROGRESS, VisitStatus.CANCELLED],
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
        verbose_name=_('المعرّف'),
    )
    patient = models.ForeignKey(
        'users.PatientProfile',
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name=_('المريض'),
    )
    nurse = models.ForeignKey(
        'users.NurseProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        verbose_name=_('الممرض/ة'),
    )
    status = models.CharField(
        _('الحالة'),
        max_length=15,
        choices=VisitStatus.choices,
        default=VisitStatus.PENDING,
        db_index=True,
    )
    location = gis_models.PointField(
        _('موقع الزيارة'),
        geography=True,
        srid=4326,
        help_text=_('الموقع الجغرافي للمريض عند طلب الزيارة'),
    )
    service_type = models.CharField(
        _('نوع الخدمة'),
        max_length=50,
        blank=True,
        default='',
        help_text=_('نوع الخدمة التمريضية المطلوبة'),
    )
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True,
    )

    class Meta:
        verbose_name = _('زيارة')
        verbose_name_plural = _('الزيارات')
        db_table = 'visits_visit'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Visit({str(self.id)[:8]}—{self.status})'

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
                code='invalid_status',
                params={'status': new_status},
            )

        allowed = ALLOWED_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValidationError(
                _('لا يمكن الانتقال من "%(current)s" إلى "%(new)s".'),
                code='invalid_transition',
                params={'current': self.status, 'new': new_status},
            )

        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
