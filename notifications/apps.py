from django.apps import AppConfig
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "الإشعارات"  # Notifications in Arabic

    def ready(self):
        """Initialize Firebase Admin SDK on Django startup and register signals."""
        self._init_firebase()
        self._import_signals()

    def _init_firebase(self):
        """Initialize Firebase Admin SDK with credentials from settings."""
        from django.core.exceptions import ImproperlyConfigured
        import firebase_admin
        from firebase_admin import credentials

        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
        
        if not cred_path:
            logger.warning("Firebase not configured — push notifications disabled")
            return

        try:
            # Check if Firebase is already initialized (idempotent)
            firebase_admin.get_app()
            logger.info("Firebase Admin SDK already initialized")
        except ValueError:
            # Firebase not initialized yet
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Firebase Admin SDK: %s", str(e))
                # In production, we should fail fast, but in dev we can continue
                if not settings.DEBUG:
                    raise ImproperlyConfigured(
                        f"Failed to initialize Firebase: {str(e)}"
                    )

    def _import_signals(self):
        """Import signals to register signal handlers."""
        import notifications.signals  # noqa: F401
        logger.info("Notification signals registered")
