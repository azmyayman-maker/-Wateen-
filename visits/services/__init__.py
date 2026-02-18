"""
Services package for the visits app.
Re-exports all service functions for backward compatibility.
"""

from visits.services.matching import GeoMatchingService, GEO_KEY

__all__ = ["create_visit_request", "GeoMatchingService", "GEO_KEY"]


def __getattr__(name):
    """Lazy import to avoid importing Django models when not needed."""
    if name == "create_visit_request":
        from visits.services.visit import create_visit_request

        return create_visit_request
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
