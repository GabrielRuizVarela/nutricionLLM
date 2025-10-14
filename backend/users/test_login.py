"""
Tests for User Login (US2)
Following TDD approach - these tests are written before implementation.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestUserLogin:
    """Test suite for user login functionality (US2)"""

    def setup_method(self):
        """Set up test client and create a test user before each test"""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'

        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_successful_login_with_valid_credentials(self):
        """
        Test that a user can login with valid credentials.
        AC: On successful login, the frontend receives an authentication token.
        """
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert len(response.data['token']) > 0

    def test_login_returns_user_info(self):
        """
        Test that login returns user information along with token.
        AC: The user is redirected (with token stored).
        """
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user_id' in response.data
        assert 'email' in response.data
        assert response.data['email'] == 'test@example.com'

    def test_login_with_incorrect_password(self):
        """
        Test that login fails with incorrect password.
        AC: Invalid credentials display: "Incorrect email or password."
        """
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
        error_message = response.data['error'].lower()
        assert 'incorrect' in error_message and 'password' in error_message

    def test_login_with_incorrect_email(self):
        """
        Test that login fails with non-existent email.
        AC: Invalid credentials display: "Incorrect email or password."
        """
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
        error_message = response.data['error'].lower()
        assert 'incorrect' in error_message and ('email' in error_message or 'password' in error_message)

    def test_login_requires_email(self):
        """
        Test that login requires email field.
        AC: The login form requires email and password.
        """
        data = {
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_requires_password(self):
        """
        Test that login requires password field.
        AC: The login form requires email and password.
        """
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_empty_email(self):
        """Test that login fails with empty email"""
        data = {
            'email': '',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_empty_password(self):
        """Test that login fails with empty password"""
        data = {
            'email': 'test@example.com',
            'password': ''
        }
        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_token_can_be_used_for_authentication(self):
        """
        Test that the returned token can be used for authenticated requests.
        AC: The token is stored in localStorage for subsequent API requests.
        """
        # Login to get token
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        token = response.data['token']

        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        profile_response = self.client.get('/api/profile/')

        assert profile_response.status_code == status.HTTP_200_OK

    def test_multiple_logins_return_same_token(self):
        """
        Test that multiple logins for the same user return the same token.
        This ensures token consistency.
        """
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        # First login
        response1 = self.client.post(self.login_url, data, format='json')
        token1 = response1.data['token']

        # Second login
        response2 = self.client.post(self.login_url, data, format='json')
        token2 = response2.data['token']

        assert token1 == token2
