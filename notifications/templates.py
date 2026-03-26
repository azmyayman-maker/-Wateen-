"""
Notification Templates — Bilingual (Arabic/English) template registry for push notifications.
"""

from typing import Tuple

# Template registry keyed by NotificationEventType
# Each entry contains title and body in both Arabic and English
# Uses str.format() placeholders for variable interpolation
NOTIFICATION_TEMPLATES = {
    "NURSE_ASSIGNED": {
        "title_ar": "تحديث الزيارة",
        "title_en": "Visit Update",
        "body_ar": "تم تعيين الممرض/ة {nurse_name} لزيارتك",
        "body_en": "Your nurse {nurse_name} has been assigned to your visit",
    },
    "NURSE_EN_ROUTE": {
        "title_ar": "الممرض/ة في الطريق",
        "title_en": "Nurse En Route",
        "body_ar": "الممرض/ة {nurse_name} في الطريق إليك",
        "body_en": "Your nurse {nurse_name} is on the way",
    },
    "NURSE_ARRIVED": {
        "title_ar": "وصول الممرض/ة",
        "title_en": "Nurse Arrived",
        "body_ar": "وصلت الممرض/ة إلى موقعك",
        "body_en": "Your nurse has arrived at your location",
    },
    "VISIT_COMPLETED": {
        "title_ar": "اكتملت الزيارة",
        "title_en": "Visit Completed",
        "body_ar": "تمت زيارتك بنجاح. شكراً لاختيارك وتين",
        "body_en": "Your visit has been completed successfully. Thank you for choosing Wateen",
    },
    "PAYMENT_SETTLED": {
        "title_ar": "تسوية مالية",
        "title_en": "Payment Settled",
        "body_ar": "تم تحويل مبلغ {amount} ج.م إلى محفظة وكالتك",
        "body_en": "Payment of {amount} EGP has been settled to your agency wallet",
    },
    "DISPATCH_OFFER": {
        "title_ar": "طلب زيارة جديد",
        "title_en": "New Visit Request",
        "body_ar": "لديك طلب زيارة جديد — استجب الآن",
        "body_en": "You have a new visit request — respond now",
    },
    "VISIT_CANCELLED": {
        "title_ar": "تم إلغاء الزيارة",
        "title_en": "Visit Cancelled",
        "body_ar": "تم إلغاء الزيارة",
        "body_en": "The visit has been cancelled",
    },
    "SOS_ALERT": {
        "title_ar": "🚨 تنبيه طوارئ",
        "title_en": "🚨 SOS Alert",
        "body_ar": "تنبيه طوارئ — يرجى التحقق فوراً",
        "body_en": "Emergency alert — please check immediately",
    },
}


def render_template(event_type: str, language: str = "ar", **context) -> Tuple[str, str]:
    """
    Render a notification template for the given event type and language.
    
    Args:
        event_type: The NotificationEventType value (e.g., "NURSE_ASSIGNED")
        language: The language code ("ar" or "en")
        **context: Variables to interpolate into the template
    
    Returns:
        Tuple of (title, body)
    
    Raises:
        KeyError: If event_type is not found or required format variables are missing
    """
    if event_type not in NOTIFICATION_TEMPLATES:
        raise KeyError(f"Unknown event type: {event_type}")
    
    template = NOTIFICATION_TEMPLATES[event_type]
    title_key = f"title_{language}"
    body_key = f"body_{language}"
    
    title = template[title_key].format(**context)
    body = template[body_key].format(**context)
    
    return title, body
