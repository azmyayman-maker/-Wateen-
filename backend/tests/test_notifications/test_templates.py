"""
Unit tests for notification templates.
"""

import pytest

from notifications.models import NotificationEventType
from notifications.templates import render_template


@pytest.mark.django_db
class TestRenderTemplate:
    """Tests for render_template function."""

    def test_render_template_nurse_assigned_arabic(self):
        """Test NURSE_ASSIGNED template in Arabic."""
        title, body = render_template("NURSE_ASSIGNED", "ar", nurse_name="أحمد")
        assert title == "تحديث الزيارة"
        assert "أحمد" in body

    def test_render_template_nurse_assigned_english(self):
        """Test NURSE_ASSIGNED template in English."""
        title, body = render_template("NURSE_ASSIGNED", "en", nurse_name="Ahmed")
        assert title == "Visit Update"
        assert "Ahmed" in body

    def test_render_template_payment_settled_arabic(self):
        """Test PAYMENT_SETTLED template in Arabic."""
        title, body = render_template("PAYMENT_SETTLED", "ar", amount="350.00")
        assert "350.00 ج.م" in body

    def test_render_template_payment_settled_english(self):
        """Test PAYMENT_SETTLED template in English."""
        title, body = render_template("PAYMENT_SETTLED", "en", amount="350.00")
        assert "350.00 EGP" in body

    def test_render_template_all_event_types_arabic(self):
        """All event types should render successfully in Arabic."""
        event_types = [choice[0] for choice in NotificationEventType.choices]
        for event_type in event_types:
            # Each template needs at least some context
            context = {"nurse_name": "test", "amount": "100"}
            title, body = render_template(event_type, "ar", **context)
            assert title is not None and title != ""
            assert body is not None and body != ""

    def test_render_template_all_event_types_english(self):
        """All event types should render successfully in English."""
        event_types = [choice[0] for choice in NotificationEventType.choices]
        for event_type in event_types:
            context = {"nurse_name": "test", "amount": "100"}
            title, body = render_template(event_type, "en", **context)
            assert title is not None and title != ""
            assert body is not None and body != ""

    def test_render_template_missing_variable_raises_key_error(self):
        """Missing required template variables should raise KeyError."""
        with pytest.raises(KeyError):
            render_template("NURSE_ASSIGNED", "ar")  # Missing nurse_name

    def test_render_template_unknown_event_type_raises_key_error(self):
        """Unknown event type should raise KeyError."""
        with pytest.raises(KeyError):
            render_template("INVALID_EVENT", "ar", nurse_name="test")

    def test_render_template_returns_tuple(self):
        """render_template should return a tuple of 2 elements."""
        result = render_template("NURSE_ASSIGNED", "ar", nurse_name="test")
        assert isinstance(result, tuple)
        assert len(result) == 2
