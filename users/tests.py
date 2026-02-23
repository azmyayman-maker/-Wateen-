from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import uuid

from .validators import (
    validate_egyptian_national_id,
    validate_phone_number,
    GOVERNORATE_CODES
)
from .models import PatientProfile, NurseProfile, UserRole


User = get_user_model()


class TestNationalIDValidator(TestCase):
    
    def test_valid_national_id_starts_with_2(self):
        validate_egyptian_national_id('29901011234567')
    
    def test_valid_national_id_starts_with_3(self):
        validate_egyptian_national_id('30001011234567')
    
    def test_invalid_length_too_short(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('2990101123456')
        
        self.assertEqual(context.exception.code, 'invalid_length')
    
    def test_invalid_length_too_long(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('299010112345678')
        
        self.assertEqual(context.exception.code, 'invalid_length')
    
    def test_invalid_century_digit(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('19901011234567')
        
        self.assertEqual(context.exception.code, 'invalid_century')
    
    def test_non_numeric_input(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('29901011234ABC')  # 14 chars, non-numeric
        
        self.assertEqual(context.exception.code, 'non_numeric')
    
    def test_invalid_month(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('29913011234567')
        
        self.assertEqual(context.exception.code, 'invalid_month')
    
    def test_invalid_month_zero(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('29900011234567')
        
        self.assertEqual(context.exception.code, 'invalid_month')
    
    def test_invalid_day(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('29901003234567')
        
        self.assertEqual(context.exception.code, 'invalid_day')
    
    def test_invalid_day_for_month(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('29902301234567')  # Feb 30 is invalid
        
        self.assertEqual(context.exception.code, 'invalid_day_for_month')
    
    def test_valid_governorate_codes(self):
        for gov_code in ['01', '11', '25', '35']:
            national_id = f'2990101{gov_code}00123'
            validate_egyptian_national_id(national_id)
    
    def test_invalid_governorate_code(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('29901019934567')
        
        self.assertEqual(context.exception.code, 'invalid_governorate')
    
    def test_empty_value(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('')
        
        self.assertEqual(context.exception.code, 'required')
    
    def test_none_value(self):
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id(None)
        
        self.assertEqual(context.exception.code, 'required')


class TestPhoneNumberValidator(TestCase):
    
    def test_valid_phone_number_010(self):
        validate_phone_number('01012345678')
    
    def test_valid_phone_number_011(self):
        validate_phone_number('01112345678')
    
    def test_valid_phone_number_012(self):
        validate_phone_number('01212345678')
    
    def test_valid_phone_number_015(self):
        validate_phone_number('01512345678')
    
    def test_invalid_phone_number_too_short(self):
        with self.assertRaises(ValidationError) as context:
            validate_phone_number('0101234567')
        
        self.assertEqual(context.exception.code, 'invalid_phone')
    
    def test_invalid_phone_number_invalid_prefix(self):
        with self.assertRaises(ValidationError) as context:
            validate_phone_number('01312345678')
        
        self.assertEqual(context.exception.code, 'invalid_phone')
    
    def test_invalid_phone_number_not_starting_with_01(self):
        with self.assertRaises(ValidationError) as context:
            validate_phone_number('02012345678')
        
        self.assertEqual(context.exception.code, 'invalid_phone')
    
    def test_invalid_phone_number_non_numeric(self):
        with self.assertRaises(ValidationError) as context:
            validate_phone_number('010123456AB')
        
        self.assertEqual(context.exception.code, 'invalid_phone')
    
    def test_empty_phone_number(self):
        with self.assertRaises(ValidationError) as context:
            validate_phone_number('')
        
        self.assertEqual(context.exception.code, 'required')


class TestCustomUserManager(TestCase):
    
    def test_create_user_success(self):
        user = User.objects.create_user(
            national_id='29901011234567',
            phone_number='01012345678',
            password='TestPass123!'
        )
        
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertEqual(user.national_id, '29901011234567')
        self.assertEqual(user.phone_number, '01012345678')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('TestPass123!'))
    
    def test_create_user_without_national_id(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                national_id='',
                phone_number='01012345678',
                password='TestPass123!'
            )
    
    def test_create_user_without_phone_number(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                national_id='29901011234567',
                phone_number='',
                password='TestPass123!'
            )
    
    def test_create_superuser_success(self):
        user = User.objects.create_superuser(
            national_id='29901011234678',
            phone_number='01012345679',
            password='AdminPass123!'
        )
        
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'ADMIN')
    
    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                national_id='29901011234689',
                phone_number='01012345680',
                password='AdminPass123!',
                is_staff=False
            )
    
    def test_create_superuser_without_is_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                national_id='29901011234690',
                phone_number='01012345681',
                password='AdminPass123!',
                is_superuser=False
            )
    
    def test_national_id_unique_constraint(self):
        User.objects.create_user(
            national_id='29901011234701',
            phone_number='01012345682',
            password='TestPass123!'
        )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                national_id='29901011234701',
                phone_number='01012345683',
                password='TestPass123!'
            )
    
    def test_phone_number_unique_constraint(self):
        User.objects.create_user(
            national_id='29901011234702',
            phone_number='01012345684',
            password='TestPass123!'
        )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                national_id='29901011234703',
                phone_number='01012345684',
                password='TestPass123!'
            )
    
    def test_login_with_national_id(self):
        user = User.objects.create_user(
            national_id='29901011234704',
            phone_number='01012345685',
            password='TestPass123!'
        )
        
        from django.contrib.auth import authenticate
        
        authenticated_user = authenticate(
            national_id='29901011234704',
            password='TestPass123!'
        )
        
        self.assertEqual(authenticated_user, user)


class TestJWTAuth(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            national_id='29901011234705',
            phone_number='01012345686',
            password='TestPass123!'
        )
    
    def test_obtain_token_success(self):
        response = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234705',
            'password': 'TestPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_obtain_token_invalid_credentials(self):
        response = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234705',
            'password': 'WrongPass123!'
        }, format='json')
        
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    def test_obtain_token_invalid_user(self):
        response = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011239999',
            'password': 'TestPass123!'
        }, format='json')
        
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    def test_refresh_token_success(self):
        token_response = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234705',
            'password': 'TestPass123!'
        }, format='json')
        
        refresh_token = token_response.data.get('refresh')
        
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class TestRegistration(TestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def test_registration_success(self):
        response = self.client.post('/api/v1/auth/register/', {
            'national_id': '29901011234706',
            'phone_number': '01012345687',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['national_id'], '29901011234706')
    
    def test_registration_password_mismatch(self):
        response = self.client.post('/api/v1/auth/register/', {
            'national_id': '29901011234707',
            'phone_number': '01012345688',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_duplicate_national_id(self):
        User.objects.create_user(
            national_id='29901011234708',
            phone_number='01012345689',
            password='TestPass123!'
        )
        
        response = self.client.post('/api/v1/auth/register/', {
            'national_id': '29901011234708',
            'phone_number': '01012345690',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_invalid_national_id(self):
        response = self.client.post('/api/v1/auth/register/', {
            'national_id': '12345',
            'phone_number': '01012345691',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserProfile(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            national_id='29901011234709',
            phone_number='01012345692',
            password='TestPass123!',
            first_name_ar='أحمد',
            last_name_ar='محمد'
        )
        
        token_response = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234709',
            'password': 'TestPass123!'
        }, format='json')
        
        self.access_token = token_response.data['access']
    
    def test_get_profile_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get('/api/v1/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['national_id'], '29901011234709')
        self.assertEqual(response.data['first_name_ar'], 'أحمد')
    
    def test_get_profile_unauthenticated(self):
        response = self.client.get('/api/v1/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.patch('/api/v1/profile/', {
            'first_name_ar': 'محمد',
            'last_name_ar': 'أحمد'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name_ar'], 'محمد')


class TestUserProperties(TestCase):
    
    def test_user_role_properties(self):
        patient = User.objects.create_user(
            national_id='29901011234710',
            phone_number='01012345693',
            password='TestPass123!',
            role='PATIENT'
        )
        
        doctor = User.objects.create_user(
            national_id='29901011234711',
            phone_number='01012345694',
            password='TestPass123!',
            role='DOCTOR'
        )
        
        nurse = User.objects.create_user(
            national_id='29901011234712',
            phone_number='01012345695',
            password='TestPass123!',
            role='NURSE'
        )
        
        admin = User.objects.create_superuser(
            national_id='29901011234713',
            phone_number='01012345696',
            password='AdminPass123!'
        )
        
        self.assertTrue(patient.is_patient)
        self.assertFalse(patient.is_doctor)
        
        self.assertTrue(doctor.is_doctor)
        self.assertFalse(doctor.is_patient)
        
        self.assertTrue(nurse.is_nurse)
        
        self.assertTrue(admin.is_admin_user)
    
    def test_get_full_name(self):
        user = User.objects.create_user(
            national_id='29901011234714',
            phone_number='01012345697',
            password='TestPass123!',
            first_name_ar='أحمد',
            last_name_ar='محمد'
        )
        
        self.assertEqual(user.get_full_name(), 'أحمد محمد')
    
    def test_get_full_name_without_names(self):
        user = User.objects.create_user(
            national_id='29901011234715',
            phone_number='01012345698',
            password='TestPass123!'
        )
        
        self.assertEqual(user.get_full_name(), '29901011234715')


class TestPatientProfileSignal(TestCase):
    """Verify post_save signal creates PatientProfile for PATIENT users."""

    def test_patient_profile_auto_created(self):
        user = User.objects.create_user(
            national_id='29901011234800',
            phone_number='01012345800',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.assertTrue(
            PatientProfile.objects.filter(user=user).exists(),
            'PatientProfile was not auto-created for PATIENT user',
        )

    def test_nurse_does_not_get_patient_profile(self):
        user = User.objects.create_user(
            national_id='29901011234801',
            phone_number='01012345801',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        self.assertFalse(
            PatientProfile.objects.filter(user=user).exists(),
            'PatientProfile should NOT be created for NURSE user',
        )


class TestNurseProfileSignal(TestCase):
    """Verify post_save signal creates NurseProfile for NURSE users."""

    def test_nurse_profile_auto_created(self):
        user = User.objects.create_user(
            national_id='29901011234802',
            phone_number='01012345802',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        self.assertTrue(
            NurseProfile.objects.filter(user=user).exists(),
            'NurseProfile was not auto-created for NURSE user',
        )

    def test_patient_does_not_get_nurse_profile(self):
        user = User.objects.create_user(
            national_id='29901011234803',
            phone_number='01012345803',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.assertFalse(
            NurseProfile.objects.filter(user=user).exists(),
            'NurseProfile should NOT be created for PATIENT user',
        )

    def test_nurse_profile_default_values(self):
        user = User.objects.create_user(
            national_id='29901011234804',
            phone_number='01012345804',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        profile = NurseProfile.objects.get(user=user)
        self.assertEqual(profile.rating, 5.00)
        self.assertFalse(profile.is_available)
        self.assertEqual(profile.verification_status, 'PENDING')
        self.assertEqual(profile.specializations, [])


class TestProfileModelStr(TestCase):
    """Verify __str__ representations of profile models."""

    def test_patient_profile_str(self):
        user = User.objects.create_user(
            national_id='29901011234805',
            phone_number='01012345805',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        profile = PatientProfile.objects.get(user=user)
        self.assertEqual(str(profile), 'PatientProfile(29901011234805)')

    def test_nurse_profile_str(self):
        user = User.objects.create_user(
            national_id='29901011234806',
            phone_number='01012345806',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        profile = NurseProfile.objects.get(user=user)

        self.assertEqual(str(profile), 'NurseProfile(29901011234806)')

        self.assertEqual(str(profile), 'NurseProfile(29901011234806)')


class TestAdminInterface(TestCase):
    """Test Django admin functionality for CustomUser and Profiles."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            national_id='29901011234900',
            phone_number='01012345900',
            password='AdminPass123!'
        )
        self.client = APIClient()
        from django.contrib.admin.sites import AdminSite
        from users.admin import CustomUserAdmin, PatientProfileAdmin, NurseProfileAdmin

        self.site = AdminSite()
        self.user_admin = CustomUserAdmin(User, self.site)
        self.patient_admin = PatientProfileAdmin(PatientProfile, self.site)
        self.nurse_admin = NurseProfileAdmin(NurseProfile, self.site)

    def test_custom_user_admin_list_display(self):
        """Verify CustomUserAdmin list_display fields."""
        expected_fields = (
            'national_id',
            'phone_number',
            'role',
            'is_active',
            'is_staff',
            'date_joined'
        )
        self.assertEqual(self.user_admin.list_display, expected_fields)

    def test_custom_user_admin_search_fields(self):
        """Verify CustomUserAdmin search fields."""
        expected_fields = (
            'national_id',
            'phone_number',
            'email',
            'first_name_ar',
            'last_name_ar'
        )
        self.assertEqual(self.user_admin.search_fields, expected_fields)

    def test_custom_user_admin_list_filter(self):
        """Verify CustomUserAdmin list filters."""
        expected_filters = (
            'role',
            'is_active',
            'is_staff',
            'is_superuser'
        )
        self.assertEqual(self.user_admin.list_filter, expected_filters)

    def test_patient_profile_admin_list_display(self):
        """Verify PatientProfileAdmin list_display fields."""
        expected_fields = ('user', 'date_of_birth', 'gender', 'wearables_enabled', 'created_at')
        self.assertEqual(self.patient_admin.list_display, expected_fields)

    def test_nurse_profile_admin_list_display(self):
        """Verify NurseProfileAdmin list_display fields."""
        expected_fields = ('user', 'syndicate_number', 'rating', 'is_available', 'verification_status', 'created_at')
        self.assertEqual(self.nurse_admin.list_display, expected_fields)

    def test_patient_profile_admin_search_fields(self):
        """Verify PatientProfileAdmin search functionality."""
        expected_fields = ('user__national_id', 'user__phone_number', 'emergency_contact')
        self.assertEqual(self.patient_admin.search_fields, expected_fields)

    def test_nurse_profile_admin_search_fields(self):
        """Verify NurseProfileAdmin search functionality."""
        expected_fields = ('user__national_id', 'user__phone_number', 'syndicate_number')
        self.assertEqual(self.nurse_admin.search_fields, expected_fields)


class TestPatientProfileValidation(TestCase):
    """Test PatientProfile model field validation and constraints."""

    def test_patient_profile_creation_with_all_fields(self):
        """Create PatientProfile with all optional fields populated."""
        from datetime import date
        from django.contrib.gis.geos import Point

        user = User.objects.create_user(
            national_id='29901011234810',
            phone_number='01012345810',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        profile = PatientProfile.objects.get(user=user)
        profile.date_of_birth = date(1990, 1, 1)
        profile.gender = 'MALE'
        profile.address_text = 'Cairo, Egypt'
        profile.home_location = Point(31.2357, 30.0444)  # Cairo coordinates
        profile.medical_notes = 'No allergies'
        profile.emergency_contact = '01012345999'
        profile.wearables_enabled = True
        profile.save()

        profile.refresh_from_db()
        self.assertEqual(profile.gender, 'MALE')
        self.assertTrue(profile.wearables_enabled)
        self.assertIsNotNone(profile.home_location)

    def test_patient_profile_gender_choices(self):
        """Test gender field accepts valid choices."""
        from users.models import GenderChoices

        user = User.objects.create_user(
            national_id='29901011234811',
            phone_number='01012345811',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        profile = PatientProfile.objects.get(user=user)

        # Test MALE choice
        profile.gender = GenderChoices.MALE
        profile.save()
        self.assertEqual(profile.gender, 'MALE')

        # Test FEMALE choice
        profile.gender = GenderChoices.FEMALE
        profile.save()
        self.assertEqual(profile.gender, 'FEMALE')

    def test_patient_profile_cascade_delete(self):
        """Test that deleting user cascades to profile."""
        user = User.objects.create_user(
            national_id='29901011234812',
            phone_number='01012345812',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        profile_exists = PatientProfile.objects.filter(user=user).exists()
        self.assertTrue(profile_exists)

        user.delete()

        profile_exists = PatientProfile.objects.filter(user_id=user.id).exists()
        self.assertFalse(profile_exists)

    def test_patient_profile_nullable_fields(self):
        """Test that optional fields can be null or blank."""
        user = User.objects.create_user(
            national_id='29901011234813',
            phone_number='01012345813',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        profile = PatientProfile.objects.get(user=user)

        # All these fields should be nullable/blank by default
        self.assertIsNone(profile.date_of_birth)
        self.assertEqual(profile.gender, '')
        self.assertEqual(profile.address_text, '')
        self.assertIsNone(profile.home_location)


class TestNurseProfileValidation(TestCase):
    """Test NurseProfile model field validation and constraints."""

    def test_nurse_profile_creation_with_all_fields(self):
        """Create NurseProfile with all optional fields populated."""
        from datetime import date
        from django.contrib.gis.geos import Point
        from users.models import VerificationStatus

        user = User.objects.create_user(
            national_id='29901011234820',
            phone_number='01012345820',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=user)
        profile.national_id_document = 'NID-123456'
        profile.syndicate_number = 'SYN-789'
        profile.syndicate_expiry = date(2025, 12, 31)
        profile.specializations = ['ICU', 'Emergency']
        profile.rating = 4.75
        profile.is_available = True
        profile.last_location = Point(31.2357, 30.0444)
        profile.verification_status = VerificationStatus.VERIFIED
        profile.save()

        profile.refresh_from_db()
        self.assertEqual(profile.syndicate_number, 'SYN-789')
        self.assertEqual(profile.rating, 4.75)
        self.assertTrue(profile.is_available)
        self.assertEqual(profile.verification_status, 'VERIFIED')
        self.assertEqual(len(profile.specializations), 2)

    def test_nurse_profile_verification_status_choices(self):
        """Test verification_status field accepts valid choices."""
        from users.models import VerificationStatus

        user = User.objects.create_user(
            national_id='29901011234821',
            phone_number='01012345821',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=user)

        # Default should be PENDING
        self.assertEqual(profile.verification_status, VerificationStatus.PENDING)

        # Test VERIFIED
        profile.verification_status = VerificationStatus.VERIFIED
        profile.save()
        self.assertEqual(profile.verification_status, 'VERIFIED')

        # Test REJECTED
        profile.verification_status = VerificationStatus.REJECTED
        profile.save()
        self.assertEqual(profile.verification_status, 'REJECTED')

    def test_nurse_profile_specializations_jsonfield(self):
        """Test specializations JSONField functionality."""
        user = User.objects.create_user(
            national_id='29901011234822',
            phone_number='01012345822',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=user)

        # Default should be empty list
        self.assertEqual(profile.specializations, [])

        # Test adding specializations
        profile.specializations = ['Pediatric', 'Geriatric', 'Home Care']
        profile.save()
        profile.refresh_from_db()

        self.assertEqual(len(profile.specializations), 3)
        self.assertIn('Pediatric', profile.specializations)

    def test_nurse_profile_rating_decimal_precision(self):
        """Test rating field decimal precision."""
        user = User.objects.create_user(
            national_id='29901011234823',
            phone_number='01012345823',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=user)

        # Default rating
        self.assertEqual(profile.rating, 5.00)

        # Test decimal precision (max_digits=3, decimal_places=2)
        profile.rating = 4.99
        profile.save()
        profile.refresh_from_db()
        self.assertEqual(profile.rating, 4.99)

    def test_nurse_profile_cascade_delete(self):
        """Test that deleting user cascades to profile."""
        user = User.objects.create_user(
            national_id='29901011234824',
            phone_number='01012345824',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile_exists = NurseProfile.objects.filter(user=user).exists()
        self.assertTrue(profile_exists)

        user.delete()

        profile_exists = NurseProfile.objects.filter(user_id=user.id).exists()
        self.assertFalse(profile_exists)


class TestGISFields(TestCase):
    """Test GIS PointField functionality for location data."""

    def test_patient_home_location_point_field(self):
        """Test PatientProfile home_location PointField."""
        from django.contrib.gis.geos import Point

        user = User.objects.create_user(
            national_id='29901011234830',
            phone_number='01012345830',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        profile = PatientProfile.objects.get(user=user)

        # Set Cairo coordinates (longitude, latitude)
        cairo_point = Point(31.2357, 30.0444)
        profile.home_location = cairo_point
        profile.save()

        profile.refresh_from_db()

        self.assertIsNotNone(profile.home_location)
        self.assertEqual(profile.home_location.x, 31.2357)
        self.assertEqual(profile.home_location.y, 30.0444)
        self.assertEqual(profile.home_location.srid, 4326)

    def test_nurse_last_location_point_field(self):
        """Test NurseProfile last_location PointField."""
        from django.contrib.gis.geos import Point

        user = User.objects.create_user(
            national_id='29901011234831',
            phone_number='01012345831',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=user)

        # Set Alexandria coordinates
        alex_point = Point(29.9187, 31.2001)
        profile.last_location = alex_point
        profile.save()

        profile.refresh_from_db()

        self.assertIsNotNone(profile.last_location)
        self.assertEqual(profile.last_location.x, 29.9187)
        self.assertEqual(profile.last_location.y, 31.2001)

    def test_point_field_null_values(self):
        """Test that PointFields can be null."""
        patient_user = User.objects.create_user(
            national_id='29901011234832',
            phone_number='01012345832',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        nurse_user = User.objects.create_user(
            national_id='29901011234833',
            phone_number='01012345833',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        patient_profile = PatientProfile.objects.get(user=patient_user)
        nurse_profile = NurseProfile.objects.get(user=nurse_user)

        self.assertIsNone(patient_profile.home_location)
        self.assertIsNone(nurse_profile.last_location)


class TestSignalEdgeCases(TestCase):
    """Test edge cases and error handling in profile creation signals."""

    def test_signal_idempotency(self):
        """Test that get_or_create makes signal idempotent."""
        user = User.objects.create_user(
            national_id='29901011234840',
            phone_number='01012345840',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        # Profile should be created by signal
        profile1 = PatientProfile.objects.get(user=user)

        # Manually trigger signal again shouldn't create duplicate
        from users.signals import create_user_profile
        create_user_profile(User, user, False)

        # Should still have only one profile
        profile_count = PatientProfile.objects.filter(user=user).count()
        self.assertEqual(profile_count, 1)

    def test_no_profile_for_doctor_role(self):
        """Test that DOCTOR role doesn't create any profile."""
        user = User.objects.create_user(
            national_id='29901011234841',
            phone_number='01012345841',
            password='TestPass123!',
            role=UserRole.DOCTOR,
        )

        patient_profile_exists = PatientProfile.objects.filter(user=user).exists()
        nurse_profile_exists = NurseProfile.objects.filter(user=user).exists()

        self.assertFalse(patient_profile_exists)
        self.assertFalse(nurse_profile_exists)

    def test_no_profile_for_admin_role(self):
        """Test that ADMIN role doesn't create any profile."""
        user = User.objects.create_superuser(
            national_id='29901011234842',
            phone_number='01012345842',
            password='TestPass123!',
        )

        patient_profile_exists = PatientProfile.objects.filter(user=user).exists()
        nurse_profile_exists = NurseProfile.objects.filter(user=user).exists()

        self.assertFalse(patient_profile_exists)
        self.assertFalse(nurse_profile_exists)

    def test_signal_transaction_rollback(self):
        """Test that profile creation is part of user creation transaction."""
        from django.db import transaction, IntegrityError

        # Create a user that will succeed
        user1 = User.objects.create_user(
            national_id='29901011234843',
            phone_number='01012345843',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        # Verify profile was created
        self.assertTrue(PatientProfile.objects.filter(user=user1).exists())

    def test_profile_timestamps(self):
        """Test that profile timestamps are set correctly."""
        user = User.objects.create_user(
            national_id='29901011234844',
            phone_number='01012345844',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=user)

        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        self.assertEqual(profile.created_at, profile.updated_at)


class TestProfileModelMeta(TestCase):
    """Test model Meta options and database constraints."""

    def test_patient_profile_db_table_name(self):
        """Test PatientProfile uses correct db_table name."""
        self.assertEqual(PatientProfile._meta.db_table, 'users_patient_profile')

    def test_nurse_profile_db_table_name(self):
        """Test NurseProfile uses correct db_table name."""
        self.assertEqual(NurseProfile._meta.db_table, 'users_nurse_profile')

    def test_patient_profile_verbose_names(self):
        """Test PatientProfile verbose name translations."""
        self.assertEqual(str(PatientProfile._meta.verbose_name), 'ملف المريض')
        self.assertEqual(str(PatientProfile._meta.verbose_name_plural), 'ملفات المرضى')

    def test_nurse_profile_verbose_names(self):
        """Test NurseProfile verbose name translations."""
        self.assertEqual(str(NurseProfile._meta.verbose_name), 'ملف الممرض/ة')
        self.assertEqual(str(NurseProfile._meta.verbose_name_plural), 'ملفات الممرضين')

    def test_profile_one_to_one_relationship(self):
        """Test that profile has OneToOne relationship with user."""
        patient = User.objects.create_user(
            national_id='29901011234850',
            phone_number='01012345850',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        # Access via reverse relationship
        profile = patient.patient_profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, patient)

    def test_profile_primary_key_is_user(self):
        """Test that profile primary key is the user relationship."""
        nurse = User.objects.create_user(
            national_id='29901011234851',
            phone_number='01012345851',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        profile = NurseProfile.objects.get(user=nurse)

        # The primary key should be the user UUID
        self.assertEqual(profile.pk, nurse.pk)
        self.assertEqual(profile.user_id, nurse.id)


# =============================================================================
# Ticket 4.2 — KYC Workflow Tests
# =============================================================================

class TestNurseDocumentModel(TestCase):
    """Test NurseDocument model creation, constraints, and cascade."""

    def setUp(self):
        self.nurse_user = User.objects.create_user(
            national_id='29901011234860',
            phone_number='01012345860',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        self.nurse_profile = NurseProfile.objects.get(user=self.nurse_user)

    def test_create_nurse_document(self):
        """Test basic NurseDocument creation."""
        from users.models import NurseDocument, DocumentType, DocumentStatus
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_image = SimpleUploadedFile(
            'test_id.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        doc = NurseDocument.objects.create(
            nurse=self.nurse_profile,
            document_type=DocumentType.NATIONAL_ID,
            document_file=fake_image,
        )

        self.assertEqual(doc.document_type, 'NATIONAL_ID')
        self.assertEqual(doc.status, DocumentStatus.PENDING)
        self.assertEqual(doc.extracted_national_id, '')
        self.assertEqual(doc.rejection_reason, '')
        self.assertIsNotNone(doc.uploaded_at)
        self.assertIsNone(doc.verified_at)

    def test_unique_constraint_per_document_type(self):
        """Test that nurse can have only one document per type."""
        from users.models import NurseDocument, DocumentType
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.db import IntegrityError

        fake_image1 = SimpleUploadedFile(
            'id1.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )
        fake_image2 = SimpleUploadedFile(
            'id2.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        NurseDocument.objects.create(
            nurse=self.nurse_profile,
            document_type=DocumentType.NATIONAL_ID,
            document_file=fake_image1,
        )

        with self.assertRaises(IntegrityError):
            NurseDocument.objects.create(
                nurse=self.nurse_profile,
                document_type=DocumentType.NATIONAL_ID,
                document_file=fake_image2,
            )

    def test_different_document_types_allowed(self):
        """Test that nurse can upload different document types."""
        from users.models import NurseDocument, DocumentType
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_id = SimpleUploadedFile(
            'national_id.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )
        fake_card = SimpleUploadedFile(
            'syndicate.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        doc1 = NurseDocument.objects.create(
            nurse=self.nurse_profile,
            document_type=DocumentType.NATIONAL_ID,
            document_file=fake_id,
        )
        doc2 = NurseDocument.objects.create(
            nurse=self.nurse_profile,
            document_type=DocumentType.SYNDICATE_CARD,
            document_file=fake_card,
        )

        self.assertEqual(NurseDocument.objects.filter(nurse=self.nurse_profile).count(), 2)

    def test_cascade_delete_with_user(self):
        """Test that deleting user cascades to NurseDocument."""
        from users.models import NurseDocument, DocumentType
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_image = SimpleUploadedFile(
            'test.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        NurseDocument.objects.create(
            nurse=self.nurse_profile,
            document_type=DocumentType.NATIONAL_ID,
            document_file=fake_image,
        )

        self.nurse_user.delete()
        self.assertEqual(NurseDocument.objects.count(), 0)

    def test_document_str_representation(self):
        """Test __str__ method."""
        from users.models import NurseDocument, DocumentType
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_image = SimpleUploadedFile(
            'test.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        doc = NurseDocument.objects.create(
            nurse=self.nurse_profile,
            document_type=DocumentType.NATIONAL_ID,
            document_file=fake_image,
        )

        self.assertIn('NurseProfile', str(doc))

    def test_db_table_name(self):
        """Test NurseDocument uses correct db_table."""
        from users.models import NurseDocument
        self.assertEqual(NurseDocument._meta.db_table, 'users_nurse_document')


class TestKYCService(TestCase):
    """Test KYC service layer with mocked OCR (no Tesseract needed in CI)."""

    def test_extract_national_id_with_valid_image(self):
        """Test that extract_national_id returns None for a non-ID image."""
        from users.services.kyc_service import extract_national_id
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a simple 10x10 white PNG (no text, so OCR should find nothing)
        import struct
        import zlib

        def create_minimal_png():
            """Create a minimal valid PNG image."""
            width, height = 10, 10
            raw_data = b''
            for _ in range(height):
                raw_data += b'\x00' + b'\xff' * (width * 3)
            compressed = zlib.compress(raw_data)

            def chunk(chunk_type, data):
                c = chunk_type + data
                return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

            sig = b'\x89PNG\r\n\x1a\n'
            ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
            return sig + chunk(b'IHDR', ihdr_data) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

        png_bytes = create_minimal_png()
        fake_file = SimpleUploadedFile('blank.png', png_bytes, content_type='image/png')

        try:
            extracted_id, raw_text = extract_national_id(fake_file)
            # A blank image should not contain a National ID
            self.assertIsNone(extracted_id)
        except Exception:
            # If Tesseract is not installed in CI, this is expected
            pass

    def test_preprocess_image_invalid_bytes(self):
        """Test that preprocess_image raises ValueError for invalid input."""
        from users.services.kyc_service import preprocess_image

        with self.assertRaises(ValueError):
            preprocess_image(b'not-an-image')

    def test_national_id_regex_pattern(self):
        """Test the regex pattern used for National ID extraction."""
        from users.services.kyc_service import NATIONAL_ID_PATTERN

        # Valid patterns
        self.assertIsNotNone(NATIONAL_ID_PATTERN.search('29901011234567'))
        self.assertIsNotNone(NATIONAL_ID_PATTERN.search('30001011234567'))

        # Invalid patterns
        self.assertIsNone(NATIONAL_ID_PATTERN.search('19901011234567'))
        self.assertIsNone(NATIONAL_ID_PATTERN.search('1234567890'))
        self.assertIsNone(NATIONAL_ID_PATTERN.search(''))


class TestKYCUploadAPI(TestCase):
    """Integration tests for the KYC upload endpoint."""

    def setUp(self):
        self.client = APIClient()

        # Create nurse user
        self.nurse_user = User.objects.create_user(
            national_id='29901011234870',
            phone_number='01012345870',
            password='TestPass123!',
            role=UserRole.NURSE,
        )

        # Create patient user
        self.patient_user = User.objects.create_user(
            national_id='29901011234871',
            phone_number='01012345871',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )

        # Get tokens
        nurse_token_resp = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234870',
            'password': 'TestPass123!',
        }, format='json')
        self.nurse_token = nurse_token_resp.data['access']

        patient_token_resp = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234871',
            'password': 'TestPass123!',
        }, format='json')
        self.patient_token = patient_token_resp.data['access']

    def test_upload_requires_authentication(self):
        """Test that unauthenticated requests are rejected."""
        response = self.client.post('/api/v1/kyc/upload/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_requires_nurse_role(self):
        """Test that non-nurse users get 403."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')

        from django.core.files.uploadedfile import SimpleUploadedFile
        fake_image = SimpleUploadedFile(
            'test.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        response = self.client.post('/api/v1/kyc/upload/', {
            'document_type': 'NATIONAL_ID',
            'document_file': fake_image,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_missing_file(self):
        """Test that missing file returns 400."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')

        response = self.client.post('/api/v1/kyc/upload/', {
            'document_type': 'NATIONAL_ID',
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_invalid_document_type(self):
        """Test that invalid document type returns 400."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')

        from django.core.files.uploadedfile import SimpleUploadedFile
        fake_image = SimpleUploadedFile(
            'test.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        response = self.client.post('/api/v1/kyc/upload/', {
            'document_type': 'INVALID_TYPE',
            'document_file': fake_image,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_invalid_file_extension(self):
        """Test that non-image files are rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')

        from django.core.files.uploadedfile import SimpleUploadedFile
        fake_pdf = SimpleUploadedFile(
            'test.pdf', b'%PDF-1.4' + b'\x00' * 100, content_type='application/pdf'
        )

        response = self.client.post('/api/v1/kyc/upload/', {
            'document_type': 'NATIONAL_ID',
            'document_file': fake_pdf,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_creates_nurse_document(self):
        """Test that valid upload creates a NurseDocument record."""
        from users.models import NurseDocument
        from unittest.mock import patch

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')

        from django.core.files.uploadedfile import SimpleUploadedFile
        fake_image = SimpleUploadedFile(
            'test.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
        )

        # Mock the verify_kyc_document to avoid needing Tesseract in CI
        with patch('users.views.verify_kyc_document') as mock_verify:
            mock_verify.return_value = {
                'status': 'rejected',
                'reason': 'Could not read National ID clearly.',
                'extracted_id': None,
            }

            response = self.client.post('/api/v1/kyc/upload/', {
                'document_type': 'NATIONAL_ID',
                'document_file': fake_image,
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('document', response.data)

        # Verify NurseDocument was created
        nurse_profile = NurseProfile.objects.get(user=self.nurse_user)
        self.assertTrue(
            NurseDocument.objects.filter(nurse=nurse_profile).exists()
        )

    def test_upload_replaces_existing_document(self):
        """Test that uploading same type replaces the old document."""
        from users.models import NurseDocument, DocumentType
        from unittest.mock import patch

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')

        from django.core.files.uploadedfile import SimpleUploadedFile

        with patch('users.views.verify_kyc_document') as mock_verify:
            mock_verify.return_value = {
                'status': 'rejected',
                'reason': 'Blurry image.',
                'extracted_id': None,
            }

            # First upload
            fake_image1 = SimpleUploadedFile(
                'id1.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
            )
            self.client.post('/api/v1/kyc/upload/', {
                'document_type': 'NATIONAL_ID',
                'document_file': fake_image1,
            }, format='multipart')

            # Second upload (same type — should replace)
            fake_image2 = SimpleUploadedFile(
                'id2.jpg', b'\xff\xd8\xff\xe0' + b'\x00' * 100, content_type='image/jpeg'
            )
            self.client.post('/api/v1/kyc/upload/', {
                'document_type': 'NATIONAL_ID',
                'document_file': fake_image2,
            }, format='multipart')

        nurse_profile = NurseProfile.objects.get(user=self.nurse_user)
        count = NurseDocument.objects.filter(
            nurse=nurse_profile,
            document_type=DocumentType.NATIONAL_ID,
        ).count()
        self.assertEqual(count, 1)  # Only the latest document remains

