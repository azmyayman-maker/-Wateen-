"""
Services package for the visits app.
Re-exports all service functions for backward compatibility.

T056: Exports pricing engine classes for external use.
"""

from visits.services.matching import GEO_KEY, GeoMatchingService
from visits.services.pricing import (
    MLPricingStrategy,
    PriceBreakdown,
    PricingStrategy,
    RuleBasedPricingStrategy,
    get_default_strategy,
)

__all__ = [
    "create_visit_request",
    "broadcast_visit_request",
    "GeoMatchingService",
    "GEO_KEY",
    "PricingStrategy",
    "RuleBasedPricingStrategy",
    "MLPricingStrategy",
    "PriceBreakdown",
    "get_default_strategy",
]


def __getattr__(name):
    """Lazy import to avoid importing Django models when not needed."""
    if name == "create_visit_request":
        from visits.services.visit import create_visit_request

        return create_visit_request
    elif name == "broadcast_visit_request":
        from visits.services.visit import broadcast_visit_request

        return broadcast_visit_request
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
