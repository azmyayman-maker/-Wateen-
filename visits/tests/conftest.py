import pytest
import factory
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from users.models import PatientProfile, NurseProfile, UserRole
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
        django_get_or_create = ('user',)

    user = factory.SubFactory(CustomUserFactory, role=UserRole.PATIENT)
    address_text = factory.Faker("address")
    home_location = Point(31.2357, 30.0444, srid=4326) # Cairo

class NurseProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NurseProfile
        django_get_or_create = ('user',)

    user = factory.SubFactory(CustomUserFactory, role=UserRole.NURSE)
    is_available = True
    last_location = Point(31.2357, 30.0444, srid=4326) # Cairo

class ServiceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceType

    name = factory.Sequence(lambda n: f"Service {n}")
    base_price = '100.00'
    surge_multiplier = '1.0'
    is_active = True

class VisitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Visit

    patient = factory.SubFactory(PatientProfileFactory)
    nurse = factory.SubFactory(NurseProfileFactory)
    service_type = factory.SubFactory(ServiceTypeFactory)
    status = VisitStatus.PENDING
    location = Point(31.2357, 30.0444, srid=4326)

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
    return ServiceTypeFactory(base_price='150.00')

@pytest.fixture
def visit(patient, nurse, service_type):
    return VisitFactory(
        patient=patient,
        nurse=nurse,
        service_type=service_type,
        status=VisitStatus.PENDING
    )
