"""
Tests for User Logout (US3)
Following TDD approach - these tests are written before implementation.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
class TestUserLogout:
    """Test suite for user logout functionality (US3)"""

    def setup_method(self):
        """Set up test client and create authenticated user before each test"""
        self.client = APIClient()
        self.logout_url = '/api/auth/logout/'

        # Create a test user and get token
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.test_user)

    def test_successful_logout_with_valid_token(self):
        """
        Test that an authenticated user can logout successfully.
        AC: Clicking logout removes the authentication token.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.logout_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data or 'detail' in response.data

    def test_logout_deletes_token_from_database(self):
        """
        Test that logout actually deletes the token from database.
        AC: Token is removed from localStorage (backend deletes it).
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        token_key = self.token.key

        response = self.client.post(self.logout_url)

        assert response.status_code == status.HTTP_200_OK
        # Token should no longer exist
        assert not Token.objects.filter(key=token_key).exists()

    def test_logout_requires_authentication(self):
        """
        Test that logout requires authentication.
        AC: Protected routes are no longer accessible without re-authentication.
        """
        # Try to logout without authentication
        response = self.client.post(self.logout_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_access_protected_routes_after_logout(self):
        """
        Test that protected routes are not accessible after logout.
        AC: Protected routes are no longer accessible without re-authentication.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # First, verify we can access protected route
        profile_response = self.client.get('/api/profile/')
        assert profile_response.status_code == status.HTTP_200_OK

        # Logout
        logout_response = self.client.post(self.logout_url)
        assert logout_response.status_code == status.HTTP_200_OK

        # Try to access protected route again with old token
        profile_response_after = self.client.get('/api/profile/')
        assert profile_response_after.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_already_logged_out_token(self):
        """
        Test logout behavior when token is already deleted.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # First logout
        response1 = self.client.post(self.logout_url)
        assert response1.status_code == status.HTTP_200_OK

        # Try to logout again with same token (should fail)
        response2 = self.client.post(self.logout_url)
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_invalid_token(self):
        """Test logout with invalid token format"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token_here')
        response = self.client.post(self.logout_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
