from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VisitsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "visits"
    verbose_name = _("الزيارات")

    def ready(self):
        import visits.signals  # noqa: F401 — registers signal handlers
