"""
Tests for User Registration (US1)
Following TDD approach - these tests are written before implementation.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Profile


@pytest.mark.django_db
class TestUserRegistration:
    """Test suite for user registration functionality (US1)"""

    def setup_method(self):
        """Set up test client before each test"""
        self.client = APIClient()
        self.registration_url = '/api/auth/register/'

    def test_successful_registration_with_valid_data(self):
        """
        Test that a user can register with valid email and password.
        AC: Valid email and password (min 8 characters) creates user.
        """
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'testuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert User.objects.filter(email='test@example.com').exists()

    def test_registration_creates_user_and_profile(self):
        """
        Test that registration creates both User and Profile.
        AC: Upon successful registration, a Django User and associated Profile are created.
        """
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'username': 'newuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email='newuser@example.com')
        assert hasattr(user, 'profile')
        assert isinstance(user.profile, Profile)

    def test_registration_requires_minimum_password_length(self):
        """
        Test that password must be at least 8 characters.
        AC: Password minimum 8 characters.
        """
        data = {
            'email': 'short@example.com',
            'password': 'short',
            'username': 'shortuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
        assert not User.objects.filter(email='short@example.com').exists()

    def test_registration_requires_valid_email(self):
        """
        Test that email must be in valid format.
        AC: Registration form requires a valid email.
        """
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'username': 'testuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_duplicate_email_returns_error(self):
        """
        Test that registering with existing email shows appropriate error.
        AC: If email is already registered, system displays
            "An account with this email already exists."
        """
        # Create first user
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='password123'
        )

        # Try to register with same email
        data = {
            'email': 'existing@example.com',
            'password': 'newpassword123',
            'username': 'newuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        error_message = str(response.data['email'][0])
        assert 'already exists' in error_message.lower() or 'already' in error_message.lower()

    def test_password_is_hashed(self):
        """
        Test that passwords are stored hashed, never in plain text.
        AC: Passwords are stored hashed (never in plain text).
        """
        data = {
            'email': 'secure@example.com',
            'password': 'mypassword123',
            'username': 'secureuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email='secure@example.com')
        # Password should be hashed, not plain text
        assert user.password != 'mypassword123'
        # Django uses PBKDF2 by default, check for hash format
        assert user.password.startswith('pbkdf2_sha256$')

    def test_registration_returns_auth_token(self):
        """
        Test that successful registration returns an authentication token.
        AC: User is automatically logged in (receives token).
        """
        data = {
            'email': 'tokenuser@example.com',
            'password': 'tokenpass123',
            'username': 'tokenuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert len(response.data['token']) > 0

    def test_registration_missing_email(self):
        """Test that registration fails without email"""
        data = {
            'password': 'testpass123',
            'username': 'testuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_registration_missing_password(self):
        """Test that registration fails without password"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser'
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_registration_with_empty_strings(self):
        """Test that registration fails with empty strings"""
        data = {
            'email': '',
            'password': '',
            'username': ''
        }
        response = self.client.post(self.registration_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
