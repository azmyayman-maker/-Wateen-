import pytest
from django.urls import reverse
from rest_framework import status
from visits.models import Visit, VisitStatus
from visits.payment_mock import get_mock_token

pytestmark = pytest.mark.django_db

def test_visit_lifecycle_transitions(visit):
    """
    Test direct programmatic transitions through the entire valid lifecycle.
    """
    # PENDING -> MATCHED
    visit.transition_to(VisitStatus.MATCHED)
    assert visit.status == VisitStatus.MATCHED

    # MATCHED -> ACCEPTED
    visit.transition_to(VisitStatus.ACCEPTED)
    assert visit.status == VisitStatus.ACCEPTED

    # ACCEPTED -> ON_WAY
    visit.transition_to(VisitStatus.ON_WAY)
    assert visit.status == VisitStatus.ON_WAY

    # ON_WAY -> ARRIVED
    visit.transition_to(VisitStatus.ARRIVED)
    assert visit.status == VisitStatus.ARRIVED

    # ARRIVED -> IN_PROGRESS
    visit.transition_to(VisitStatus.IN_PROGRESS)
    assert visit.status == VisitStatus.IN_PROGRESS

    # IN_PROGRESS -> COMPLETED
    visit.transition_to(VisitStatus.COMPLETED)
    assert visit.status == VisitStatus.COMPLETED


def test_invalid_lifecycle_transition(visit):
    """
    Test that invalid transitions raise ValidationError.
    PENDING -> COMPLETED is invalid.
    """
    from django.core.exceptions import ValidationError
    with pytest.raises(ValidationError):
        visit.transition_to(VisitStatus.COMPLETED)


def test_payment_webhook_completes_visit(api_client, visit, settings):
    """
    Test that the mock payment webhook can complete the visit successfully.
    """
    # Ensure webhook works (DEBUG=True)
    settings.DEBUG = True
    
    # Progress visit to IN_PROGRESS so it can be completed
    visit.transition_to(VisitStatus.MATCHED)
    visit.transition_to(VisitStatus.ACCEPTED)
    visit.transition_to(VisitStatus.ON_WAY)
    visit.transition_to(VisitStatus.ARRIVED)
    visit.transition_to(VisitStatus.IN_PROGRESS)

    url = "/api/v1/visits/payments/webhook/mock/"
    headers = {
        "HTTP_X_MOCK_TOKEN": get_mock_token(),
    }
    data = {
        "visit_id": str(visit.id),
        "status": "success",
        "amount": "150.00",
        "currency": "EGP",
        "transaction_id": "txn_12345"
    }

    response = api_client.post(url, data, format="json", **headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["payment_status"] == "completed"

    visit.refresh_from_db()
    assert visit.status == VisitStatus.COMPLETED
