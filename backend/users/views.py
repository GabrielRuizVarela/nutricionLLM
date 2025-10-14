"""
Views for user authentication and profile management.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from users.serializers import RegisterSerializer, ProfileSerializer
from users.models import Profile


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration (US1).

    POST /api/auth/register/
    - Creates a new user with email and password
    - Automatically creates associated Profile
    - Returns authentication token for automatic login
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Get or create token for automatic login
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login (US2).

    POST /api/auth/login/
    - Authenticates user with email and password
    - Returns authentication token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': 'Please provide both email and password'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Incorrect email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Authenticate with username and password
        user = authenticate(username=user.username, password=password)

        if user is None:
            return Response({
                'error': 'Incorrect email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create token
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout (US3).

    POST /api/auth/logout/
    - Deletes user's authentication token
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile (US4).

    GET /api/profile/
    - Returns current user's profile

    PATCH /api/profile/
    - Updates user's goal and dietary_preferences
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
