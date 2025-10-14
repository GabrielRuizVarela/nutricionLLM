"""
Tests for Profile Management (US4)
Following TDD approach - these tests are written before implementation.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import Profile


@pytest.mark.django_db
class TestProfileManagement:
    """Test suite for user profile management (US4)"""

    def setup_method(self):
        """Set up test client and create authenticated user before each test"""
        self.client = APIClient()
        self.profile_url = '/api/profile/'

        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_get_user_profile(self):
        """
        Test that authenticated user can retrieve their profile.
        AC: User sees profile form with goal and dietary_preferences fields.
        """
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'goal' in response.data
        assert 'dietary_preferences' in response.data
        assert 'email' in response.data

    def test_profile_is_automatically_created_on_registration(self):
        """
        Test that profile is automatically created when user registers.
        AC: Profile model is linked to user.
        """
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert Profile.objects.filter(user=self.test_user).exists()

    def test_update_profile_goal(self):
        """
        Test that user can update their nutritional goal.
        AC: User can edit goal field at any time.
        """
        data = {
            'goal': 'lose weight and gain muscle'
        }
        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['goal'] == 'lose weight and gain muscle'

        # Verify in database
        self.test_user.profile.refresh_from_db()
        assert self.test_user.profile.goal == 'lose weight and gain muscle'

    def test_update_profile_dietary_preferences(self):
        """
        Test that user can update their dietary preferences.
        AC: User can edit dietary_preferences field at any time.
        """
        data = {
            'dietary_preferences': 'vegetarian, gluten-free'
        }
        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['dietary_preferences'] == 'vegetarian, gluten-free'

        # Verify in database
        self.test_user.profile.refresh_from_db()
        assert self.test_user.profile.dietary_preferences == 'vegetarian, gluten-free'

    def test_update_both_goal_and_dietary_preferences(self):
        """
        Test that user can update both fields simultaneously.
        AC: Values are saved in the Profile model.
        """
        data = {
            'goal': 'maintain healthy weight',
            'dietary_preferences': 'vegan, low-carb'
        }
        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['goal'] == 'maintain healthy weight'
        assert response.data['dietary_preferences'] == 'vegan, low-carb'

    def test_profile_data_persists_across_sessions(self):
        """
        Test that updated profile data persists.
        AC: Updated profile data is used in subsequent recipe generation prompts.
        """
        # Update profile
        data = {
            'goal': 'build muscle',
            'dietary_preferences': 'high-protein'
        }
        self.client.patch(self.profile_url, data, format='json')

        # Retrieve profile again
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['goal'] == 'build muscle'
        assert response.data['dietary_preferences'] == 'high-protein'

    def test_profile_requires_authentication(self):
        """
        Test that profile endpoint requires authentication.
        """
        # Remove authentication
        self.client.credentials()
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_goal_can_be_empty(self):
        """
        Test that goal field can be left empty (optional).
        """
        data = {
            'goal': '',
            'dietary_preferences': 'vegetarian'
        }
        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['goal'] == ''

    def test_profile_dietary_preferences_can_be_empty(self):
        """
        Test that dietary_preferences field can be left empty (optional).
        """
        data = {
            'goal': 'lose weight',
            'dietary_preferences': ''
        }
        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['dietary_preferences'] == ''

    def test_cannot_update_other_user_profile(self):
        """
        Test that user can only access their own profile.
        """
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        # Current user should only see their own profile
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['email'] != 'other@example.com'

    def test_profile_returns_username_and_email(self):
        """
        Test that profile includes username and email (read-only).
        """
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'username' in response.data
        assert 'email' in response.data
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
