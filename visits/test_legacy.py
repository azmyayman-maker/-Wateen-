import uuid

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from rest_framework import status as http_status

from users.models import UserRole, PatientProfile
from .models import Visit, VisitStatus, ALLOWED_TRANSITIONS
from .services import create_visit_request

User = get_user_model()


class TestVisitStatusTransitions(TestCase):
    """Test the state machine logic in Visit.transition_to()."""

    def setUp(self):
        self.user = User.objects.create_user(
            national_id='29901011234900',
            phone_number='01012345900',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.patient = PatientProfile.objects.get(user=self.user)
        self.visit = Visit.objects.create(
            patient=self.patient,
            status=VisitStatus.PENDING_AGENCY,
            location=Point(31.2357, 30.0444, srid=4326),
        )

    def test_valid_transition_pending_to_pending_nurse(self):
        self.visit.transition_to(VisitStatus.PENDING_NURSE)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.status, VisitStatus.PENDING_NURSE)

    def test_valid_transition_pending_to_cancelled(self):
        self.visit.transition_to(VisitStatus.CANCELLED)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.status, VisitStatus.CANCELLED)

    def test_valid_full_happy_path(self):
        """Test the complete happy-path lifecycle."""
        transitions = [
            VisitStatus.PENDING_NURSE,
            VisitStatus.ACCEPTED,
            VisitStatus.EN_ROUTE,
            VisitStatus.IN_PROGRESS,
            VisitStatus.COMPLETED,
        ]
        for new_status in transitions:
            self.visit.transition_to(new_status)
            self.visit.refresh_from_db()
            self.assertEqual(self.visit.status, new_status)

    def test_invalid_transition_pending_to_completed(self):
        with self.assertRaises(ValidationError) as ctx:
            self.visit.transition_to(VisitStatus.COMPLETED)
        self.assertEqual(ctx.exception.code, 'invalid_transition')

    def test_invalid_transition_pending_to_in_progress(self):
        with self.assertRaises(ValidationError):
            self.visit.transition_to(VisitStatus.IN_PROGRESS)

    def test_invalid_transition_from_completed(self):
        self.visit.status = VisitStatus.COMPLETED
        self.visit.save()
        with self.assertRaises(ValidationError):
            self.visit.transition_to(VisitStatus.PENDING_AGENCY)

    def test_invalid_transition_from_cancelled(self):
        self.visit.status = VisitStatus.CANCELLED
        self.visit.save()
        with self.assertRaises(ValidationError):
            self.visit.transition_to(VisitStatus.PENDING_AGENCY)

    def test_invalid_status_value(self):
        with self.assertRaises(ValidationError) as ctx:
            self.visit.transition_to('NONEXISTENT')
        self.assertEqual(ctx.exception.code, 'invalid_status')

    def test_all_transitions_in_map(self):
        """Verify every VisitStatus value has an entry in ALLOWED_TRANSITIONS."""
        for status_value in VisitStatus.values:
            self.assertIn(status_value, ALLOWED_TRANSITIONS)


class TestCreateVisitRequestService(TestCase):
    """Test the create_visit_request service function."""

    def setUp(self):
        self.user = User.objects.create_user(
            national_id='29901011234901',
            phone_number='01012345901',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.patient = PatientProfile.objects.get(user=self.user)

    def test_create_visit_success(self):
        visit = create_visit_request(
            patient_profile=self.patient,
            latitude=30.0444,
            longitude=31.2357,
            service_type='general_nursing',
        )
        self.assertEqual(visit.status, VisitStatus.PENDING_AGENCY)
        self.assertEqual(visit.patient, self.patient)
        self.assertIsNone(visit.nurse)
        self.assertAlmostEqual(visit.location.y, 30.0444, places=4)
        self.assertAlmostEqual(visit.location.x, 31.2357, places=4)
        self.assertEqual(visit.service_type, 'general_nursing')
        self.assertIsInstance(visit.id, uuid.UUID)

    def test_create_visit_invalid_latitude(self):
        with self.assertRaises(ValidationError) as ctx:
            create_visit_request(
                patient_profile=self.patient,
                latitude=91.0,
                longitude=31.2357,
            )
        self.assertEqual(ctx.exception.code, 'invalid_latitude')

    def test_create_visit_invalid_longitude(self):
        with self.assertRaises(ValidationError) as ctx:
            create_visit_request(
                patient_profile=self.patient,
                latitude=30.0444,
                longitude=181.0,
            )
        self.assertEqual(ctx.exception.code, 'invalid_longitude')

    def test_create_visit_default_service_type(self):
        visit = create_visit_request(
            patient_profile=self.patient,
            latitude=30.0444,
            longitude=31.2357,
        )
        self.assertEqual(visit.service_type, '')


class TestVisitRequestAPI(TestCase):
    """Test the POST /api/v1/visits/request/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        # Create patient user
        self.patient_user = User.objects.create_user(
            national_id='29901011234902',
            phone_number='01012345902',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        # Create nurse user
        self.nurse_user = User.objects.create_user(
            national_id='29901011234903',
            phone_number='01012345903',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        # Get patient token
        token_resp = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234902',
            'password': 'TestPass123!',
        }, format='json')
        self.patient_token = token_resp.data['access']

        # Get nurse token
        nurse_token_resp = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234903',
            'password': 'TestPass123!',
        }, format='json')
        self.nurse_token = nurse_token_resp.data['access']

    def test_create_visit_request_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 30.0444,
            'longitude': 31.2357,
            'service_type': 'general_nursing',
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending_agency')
        self.assertAlmostEqual(response.data['latitude'], 30.0444, places=4)
        self.assertAlmostEqual(response.data['longitude'], 31.2357, places=4)
        self.assertIn('id', response.data)

    def test_create_visit_unauthenticated(self):
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 30.0444,
            'longitude': 31.2357,
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_401_UNAUTHORIZED)

    def test_create_visit_nurse_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 30.0444,
            'longitude': 31.2357,
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_403_FORBIDDEN)

    def test_create_visit_invalid_latitude(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 95.0,
            'longitude': 31.2357,
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_create_visit_missing_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.post('/api/v1/visits/request/', {}, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)


class TestVisitModel(TestCase):
    """Test Visit model properties and str representation."""

    def setUp(self):
        self.user = User.objects.create_user(
            national_id='29901011234904',
            phone_number='01012345904',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.patient = PatientProfile.objects.get(user=self.user)

    def test_visit_str(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertIn('pending_agency', str(visit))

    def test_visit_default_status(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertEqual(visit.status, VisitStatus.PENDING_AGENCY)

    def test_visit_uuid_pk(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertIsInstance(visit.id, uuid.UUID)

    def test_visit_nurse_nullable(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertIsNone(visit.nurse)
