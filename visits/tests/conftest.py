import pytest
import factory
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from users.models import (
    PatientProfile,
    NurseProfile,
    AgencyProfile,
    AgencyStatus,
    UserRole,
)
from visits.models import Visit, ServiceType, VisitStatus

User = get_user_model()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    national_id = factory.Sequence(lambda n: f"290010112{n:05d}")
    phone_number = factory.Sequence(lambda n: f"+2010{n:08d}")
    first_name_ar = factory.Faker("first_name")
    last_name_ar = factory.Faker("last_name")


class PatientProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PatientProfile
        django_get_or_create = ("user",)

    user = factory.SubFactory(CustomUserFactory, role=UserRole.PATIENT)
    address_text = factory.Faker("address")
    home_location = Point(31.2357, 30.0444, srid=4326)  # Cairo


class NurseProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NurseProfile
        django_get_or_create = ("user",)

    agency = factory.SubFactory(f"{__name__}.AgencyProfileFactory")
    user = factory.SubFactory(CustomUserFactory, role=UserRole.NURSE, agency=factory.SelfAttribute('..agency'))
    is_available = True
    last_location = Point(31.2357, 30.0444, srid=4326)  # Cairo


class AgencyProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating test AgencyProfile instances."""

    class Meta:
        model = AgencyProfile

    manager_name = factory.Sequence(lambda n: f"Test Agency {n}")
    commercial_registry = factory.Sequence(lambda n: f"CR-{n:06d}")
    moh_license_number = factory.Sequence(lambda n: f"MOH-{n:06d}")
    tax_id = factory.Sequence(lambda n: f"TAX-{n:06d}")
    status = AgencyStatus.VERIFIED
    rating = 5.00
    network_capacity = 10
    dispatch_mode = "AUTO"
    wallet_balance = 0.00


class ServiceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceType

    name = factory.Sequence(lambda n: f"Service {n}")
    base_price = "100.00"
    surge_multiplier = "1.0"
    is_active = True


class VisitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Visit

    patient = factory.SubFactory(PatientProfileFactory)
    nurse = factory.SubFactory(NurseProfileFactory)
    service_type = factory.SubFactory(ServiceTypeFactory)
    status = VisitStatus.PENDING_AGENCY
    location = Point(31.2357, 30.0444, srid=4326)
    distance_km = Decimal("5.00")
    distance_rate = Decimal("2.50")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def patient():
    return PatientProfileFactory()


@pytest.fixture
def nurse():
    return NurseProfileFactory()


@pytest.fixture
def service_type():
    return ServiceTypeFactory(base_price="150.00")


@pytest.fixture
def visit(patient, nurse, service_type):
    return VisitFactory(
        patient=patient,
        nurse=nurse,
        service_type=service_type,
        status=VisitStatus.PENDING_AGENCY,
        final_price="150.00",
    )


@pytest.fixture
def sample_agency():
    """Fixture for creating a test AgencyProfile with verified status."""
    return AgencyProfileFactory(
        manager_name="Test Agency",
        commercial_registry="TEST-123456",
        moh_license_number="MOH-TEST-001",
        tax_id="TAX-TEST-001",
        status=AgencyStatus.VERIFIED,
        wallet_balance=Decimal("1000.00"),
    )


@pytest.fixture
def sample_visit(sample_agency):
    """Fixture for creating a test Visit with agency and final_price."""
    from decimal import Decimal

    patient = PatientProfileFactory()
    service = ServiceTypeFactory(base_price="200.00")
    return VisitFactory(
        patient=patient,
        agency=sample_agency,
        nurse=None,
        service_type=service,
        status=VisitStatus.PENDING_AGENCY,
        final_price=Decimal("250.00"),
        base_price=Decimal("200.00"),
        distance_fee=Decimal("30.00"),
        distance_km=Decimal("10.00"),
        distance_rate=Decimal("2.50"),
        time_multiplier=Decimal("1.0"),
        ai_surge_coefficient=Decimal("1.0"),
    )
