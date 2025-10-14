"""
Serializers for user authentication and profile management.
"""
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from users.models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates email uniqueness and password strength.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'token')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        """
        Check that email is not already registered.
        AC: If email is already registered, system displays appropriate error.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate_password(self, value):
        """
        Check that password meets minimum length requirement.
        AC: Password minimum 8 characters.
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def get_token(self, obj):
        """Return authentication token for the newly created user"""
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def create(self, validated_data):
        """
        Create user with hashed password and associated profile.
        AC: Create Django User and associated Profile.
        AC: Passwords are stored hashed (never in plain text).
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Profile is automatically created by the post_save signal
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile management"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'username', 'email', 'goal', 'dietary_preferences',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
