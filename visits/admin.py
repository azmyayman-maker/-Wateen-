from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'nurse', 'status', 'service_type', 'created_at')
    list_filter = ('status', 'service_type')
    search_fields = ('patient__user__national_id', 'nurse__user__national_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('patient', 'nurse')
    ordering = ('-created_at',)
