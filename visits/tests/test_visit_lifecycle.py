import pytest
from visits.models import VisitStatus

pytestmark = pytest.mark.django_db


def test_visit_lifecycle_transitions(visit):
    """
    Test direct programmatic transitions through the entire valid lifecycle.
    Uses current B2B2C statuses.
    """
    # PENDING_AGENCY -> PENDING_NURSE
    visit.transition_to(VisitStatus.PENDING_NURSE)
    assert visit.status == VisitStatus.PENDING_NURSE

    # PENDING_NURSE -> ACCEPTED
    visit.transition_to(VisitStatus.ACCEPTED)
    assert visit.status == VisitStatus.ACCEPTED

    # ACCEPTED -> EN_ROUTE
    visit.transition_to(VisitStatus.EN_ROUTE)
    assert visit.status == VisitStatus.EN_ROUTE

    # EN_ROUTE -> IN_PROGRESS
    visit.transition_to(VisitStatus.IN_PROGRESS)
    assert visit.status == VisitStatus.IN_PROGRESS

    # IN_PROGRESS -> COMPLETED
    visit.transition_to(VisitStatus.COMPLETED)
    assert visit.status == VisitStatus.COMPLETED


def test_invalid_lifecycle_transition(visit):
    """
    Test that invalid transitions raise ValidationError.
    PENDING_AGENCY -> COMPLETED is invalid.
    """
    from django.core.exceptions import ValidationError

    with pytest.raises(ValidationError):
        visit.transition_to(VisitStatus.COMPLETED)
