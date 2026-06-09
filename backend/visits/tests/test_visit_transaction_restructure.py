"""
Comprehensive tests for Visit & Transaction Model Restructuring (P1-T4).

Covers:
- US1: Visit lifecycle state machine transitions
- US2: Immutable pricing snapshot enforcement
- US3: Transaction escrow ledger with auto-calculated payout
- US4: Admin readonly financial fields
- US5: GIS-enabled AgencyProfile admin

Run with:
    pytest visits/tests/test_visit_transaction_restructure.py -v --tb=short
"""

from decimal import Decimal

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

from visits.models import (
    ALLOWED_TRANSITIONS,
    Transaction,
    TransactionStatus,
    Visit,
    VisitStatus,
)

pytestmark = pytest.mark.django_db


# ============================================================================
# US1: Visit Lifecycle State Machine
# ============================================================================


class TestVisitStateMachine:
    """US1: Verify state machine transitions via ALLOWED_TRANSITIONS."""

    def test_visit_transition_happy_path(self, visit):
        """Full lifecycle: PENDING_AGENCY -> ... -> COMPLETED."""
        visit.transition_to(VisitStatus.PENDING_NURSE)
        assert visit.status == VisitStatus.PENDING_NURSE

        visit.transition_to(VisitStatus.ACCEPTED)
        assert visit.status == VisitStatus.ACCEPTED

        visit.transition_to(VisitStatus.EN_ROUTE)
        assert visit.status == VisitStatus.EN_ROUTE

        visit.transition_to(VisitStatus.IN_PROGRESS)
        assert visit.status == VisitStatus.IN_PROGRESS

        visit.transition_to(VisitStatus.COMPLETED)
        assert visit.status == VisitStatus.COMPLETED

    def test_visit_transition_invalid_raises(self, visit):
        """PENDING_AGENCY -> COMPLETED is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            visit.transition_to(VisitStatus.COMPLETED)
        assert exc_info.value.code == "invalid_transition"
        assert visit.status == VisitStatus.PENDING_AGENCY

    def test_visit_terminal_state_completed(self, visit):
        """COMPLETED is a terminal state -- no transitions allowed."""
        visit.transition_to(VisitStatus.PENDING_NURSE)
        visit.transition_to(VisitStatus.ACCEPTED)
        visit.transition_to(VisitStatus.EN_ROUTE)
        visit.transition_to(VisitStatus.IN_PROGRESS)
        visit.transition_to(VisitStatus.COMPLETED)

        with pytest.raises(ValidationError) as exc_info:
            visit.transition_to(VisitStatus.CANCELLED)
        assert exc_info.value.code == "invalid_transition"

    def test_visit_terminal_state_cancelled(self, visit):
        """CANCELLED is a terminal state -- no transitions allowed."""
        visit.transition_to(VisitStatus.CANCELLED)

        with pytest.raises(ValidationError) as exc_info:
            visit.transition_to(VisitStatus.PENDING_AGENCY)
        assert exc_info.value.code == "invalid_transition"

    def test_visit_transition_invalid_status_string(self, visit):
        """Non-existent status string raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            visit.transition_to("nonexistent_status")
        assert exc_info.value.code == "invalid_status"

    def test_cancellation_from_pending_agency(self, visit):
        """CANCELLED reachable from PENDING_AGENCY."""
        visit.transition_to(VisitStatus.CANCELLED)
        assert visit.status == VisitStatus.CANCELLED

    def test_cancellation_from_accepted(self, visit):
        """CANCELLED reachable from ACCEPTED."""
        visit.transition_to(VisitStatus.PENDING_NURSE)
        visit.transition_to(VisitStatus.ACCEPTED)
        visit.transition_to(VisitStatus.CANCELLED)
        assert visit.status == VisitStatus.CANCELLED

    def test_cancellation_from_en_route(self, visit):
        """CANCELLED reachable from EN_ROUTE."""
        visit.transition_to(VisitStatus.PENDING_NURSE)
        visit.transition_to(VisitStatus.ACCEPTED)
        visit.transition_to(VisitStatus.EN_ROUTE)
        visit.transition_to(VisitStatus.CANCELLED)
        assert visit.status == VisitStatus.CANCELLED

    def test_cancellation_from_in_progress(self, visit):
        """CANCELLED reachable from IN_PROGRESS."""
        visit.transition_to(VisitStatus.PENDING_NURSE)
        visit.transition_to(VisitStatus.ACCEPTED)
        visit.transition_to(VisitStatus.EN_ROUTE)
        visit.transition_to(VisitStatus.IN_PROGRESS)
        visit.transition_to(VisitStatus.CANCELLED)
        assert visit.status == VisitStatus.CANCELLED

    def test_allowed_transitions_map_completeness(self):
        """Every VisitStatus value must have an entry in ALLOWED_TRANSITIONS."""
        for status in VisitStatus.values:
            assert status in ALLOWED_TRANSITIONS, (
                f"Status {status} missing from ALLOWED_TRANSITIONS"
            )


# ============================================================================
# US2: Immutable Pricing Snapshot
# ============================================================================


class TestImmutablePricingSnapshot:
    """US2: Pricing fields frozen after initial save."""

    def test_pricing_immutability_blocks_final_price_update(self, visit):
        """Modifying final_price on saved Visit raises ValidationError."""
        visit.final_price = Decimal("999.99")
        with pytest.raises(ValidationError) as exc_info:
            visit.save()
        assert exc_info.value.code == "immutable_pricing"

    def test_pricing_immutability_blocks_base_price_update(self, visit):
        """Modifying base_price on saved Visit raises ValidationError."""
        visit.base_price = Decimal("999.99")
        with pytest.raises(ValidationError) as exc_info:
            visit.save()
        assert exc_info.value.code == "immutable_pricing"

    def test_pricing_immutability_blocks_ai_surge_coefficient_update(self, visit):
        """Modifying ai_surge_coefficient on saved Visit raises ValidationError."""
        visit.ai_surge_coefficient = Decimal("3.50")
        with pytest.raises(ValidationError) as exc_info:
            visit.save()
        assert exc_info.value.code == "immutable_pricing"

    def test_pricing_immutability_allows_non_pricing_update(self, visit):
        """Non-pricing field updates succeed -- status via transition_to."""
        visit.transition_to(VisitStatus.PENDING_NURSE)
        assert visit.status == VisitStatus.PENDING_NURSE

    def test_pricing_immutability_new_visit_saves_successfully(
        self, patient, nurse, service_type
    ):
        """First save with pricing fields succeeds."""
        from visits.tests.conftest import VisitFactory

        v = VisitFactory(
            patient=patient,
            nurse=nurse,
            service_type=service_type,
            base_price=Decimal("200.00"),
            final_price=Decimal("250.00"),
            distance_km=Decimal("15.00"),
            distance_rate=Decimal("2.00"),
            time_multiplier=Decimal("1.50"),
            ai_surge_coefficient=Decimal("1.10"),
        )
        assert v.pk is not None
        assert v.final_price == Decimal("250.00")

    def test_pricing_immutability_none_to_none_allowed(
        self, patient, nurse, service_type
    ):
        """None pricing fields can be resaved (None to None is not a change)."""
        from visits.tests.conftest import VisitFactory

        v = VisitFactory(
            patient=patient,
            nurse=nurse,
            service_type=service_type,
            base_price=None,
            final_price=None,
            distance_km=None,
            distance_rate=None,
            time_multiplier=None,
        )
        # Second save -- None to None should not raise
        v.reroute_attempts = 5
        v.save()  # Should not raise
        assert v.reroute_attempts == 5

    def test_immutable_fields_list_is_complete(self):
        """All expected fields are in IMMUTABLE_PRICING_FIELDS."""
        expected = {
            "base_price",
            "distance_fee",
            "distance_km",
            "distance_rate",
            "time_multiplier",
            "ai_surge_coefficient",
            "final_price",
        }
        assert set(Visit.IMMUTABLE_PRICING_FIELDS) == expected

    def test_pricing_bypass_via_update_fields_blocked(self, visit):
        """Smuggling a pricing field alongside status+updated_at is caught."""
        visit.final_price = Decimal("999.99")
        with pytest.raises(ValidationError) as exc_info:
            visit.save(update_fields=["status", "updated_at", "final_price"])
        assert exc_info.value.code == "immutable_pricing"


# ============================================================================
# US3: Transaction / Escrow Ledger
# ============================================================================


class TestTransactionEscrowLedger:
    """US3: Transaction auto-calc, status lifecycle, and FK protection."""

    def test_transaction_auto_calc_payout_default_rate(self, sample_visit):
        """Auto-calculate agency_payout at default 15% take rate."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("1000.00"),
        )
        txn.save()
        assert txn.agency_payout == Decimal("850.00")

    def test_transaction_auto_calc_payout_custom_rate(self, sample_visit):
        """Auto-calculate agency_payout with custom 20% take rate."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("1000.00"),
            wateen_take_rate=Decimal("20.00"),
        )
        txn.save()
        assert txn.agency_payout == Decimal("800.00")

    def test_transaction_auto_calc_payout_zero_amount(self, sample_visit):
        """Zero amount_paid yields zero agency_payout."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("0.00"),
        )
        txn.save()
        assert txn.agency_payout == Decimal("0.00")

    def test_transaction_settled_at_auto_set(self, sample_visit):
        """settled_at auto-set when status transitions to SETTLED."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("500.00"),
        )
        txn.save()
        assert txn.settled_at is None

        txn.status = TransactionStatus.SETTLED
        txn.save()
        assert txn.settled_at is not None

    def test_transaction_settled_at_does_not_overwrite(self, sample_visit):
        """settled_at is not overwritten on subsequent saves."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("500.00"),
            status=TransactionStatus.SETTLED,
        )
        txn.save()
        original_settled_at = txn.settled_at
        assert original_settled_at is not None

        txn.save()  # Save again
        assert txn.settled_at == original_settled_at

    def test_transaction_default_status_escrowed(self, sample_visit):
        """New Transaction defaults to ESCROWED status."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("200.00"),
        )
        assert txn.status == TransactionStatus.ESCROWED

    def test_transaction_visit_fk_protect(self, sample_visit):
        """Deleting a Visit with a Transaction raises ProtectedError."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("200.00"),
        )
        txn.save()
        with pytest.raises(ProtectedError):
            sample_visit.delete()

    def test_transaction_agency_fk_protect(self, sample_visit, sample_agency):
        """Deleting an Agency with Transactions raises ProtectedError."""
        txn = Transaction(
            visit=sample_visit,
            agency=sample_agency,
            amount_paid=Decimal("200.00"),
        )
        txn.save()
        with pytest.raises(ProtectedError):
            sample_agency.delete()

    def test_transaction_status_choices_only_three(self):
        """TransactionStatus has exactly 3 choices: ESCROWED, SETTLED, REFUNDED."""
        values = set(TransactionStatus.values)
        assert values == {"ESCROWED", "SETTLED", "REFUNDED"}

    def test_transaction_one_to_one_enforced(self, sample_visit):
        """Only one Transaction per Visit (OneToOneField)."""
        from django.db import IntegrityError

        txn1 = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("200.00"),
        )
        txn1.save()

        txn2 = Transaction(
            visit=sample_visit,
            agency=sample_visit.agency,
            amount_paid=Decimal("300.00"),
        )
        with pytest.raises(IntegrityError):
            txn2.save()


# ============================================================================
# US4: Admin Registration & Readonly Fields
# ============================================================================


class TestAdminRegistration:
    """US4 & US5: Verify admin classes have correct readonly_fields."""

    def test_visit_admin_readonly_financial_fields(self):
        """All financial fields on Visit are read-only in admin."""
        from visits.admin import VisitAdmin

        financial_fields = {
            "base_price",
            "time_multiplier",
            "distance_km",
            "distance_rate",
            "ai_surge_coefficient",
            "final_price",
        }
        assert financial_fields.issubset(set(VisitAdmin.readonly_fields))

    def test_visit_admin_list_filter_has_status_and_agency(self):
        """Visit admin has list_filter for status and agency."""
        from visits.admin import VisitAdmin

        assert "status" in VisitAdmin.list_filter
        assert "agency" in VisitAdmin.list_filter

    def test_transaction_admin_readonly_financial_fields(self):
        """All financial fields on Transaction are read-only in admin."""
        from visits.admin import TransactionAdmin

        financial_fields = {"amount_paid", "wateen_take_rate", "agency_payout"}
        assert financial_fields.issubset(set(TransactionAdmin.readonly_fields))

    def test_visit_registered_in_admin(self):
        """Visit model is registered in Django admin."""
        assert admin.site.is_registered(Visit)

    def test_transaction_registered_in_admin(self):
        """Transaction model is registered in Django admin."""
        assert admin.site.is_registered(Transaction)

    def test_agency_profile_registered_with_gis_admin(self):
        """AgencyProfile is registered with GISModelAdmin."""
        from django.contrib.gis.admin import GISModelAdmin

        from users.models import AgencyProfile

        assert admin.site.is_registered(AgencyProfile)
        admin_class = admin.site._registry[AgencyProfile]
        assert isinstance(admin_class, GISModelAdmin)


# ============================================================================
# US5: GIS-Enabled Agency Admin
# ============================================================================


class TestAgencyGISAdmin:
    """US5: AgencyProfileAdmin has GIS map widget defaults."""

    def test_agency_admin_default_coordinates(self):
        """GIS map widget defaults are centered on Egypt."""
        from users.admin import AgencyProfileAdmin

        assert AgencyProfileAdmin.default_lon == 30.8025
        assert AgencyProfileAdmin.default_lat == 26.8206
        assert AgencyProfileAdmin.default_zoom == 6
