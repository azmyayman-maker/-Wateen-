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