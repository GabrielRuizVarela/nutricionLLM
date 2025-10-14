from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    User profile model that extends the Django User model.
    Stores nutritional goals and dietary preferences for recipe generation.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    goal = models.TextField(
        blank=True,
        help_text="Nutritional goal (e.g., 'lose weight', 'gain muscle')"
    )
    dietary_preferences = models.TextField(
        blank=True,
        help_text="Dietary preferences (e.g., 'vegetarian, gluten-free')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a User is created."""
    if created:
        Profile.objects.create(user=instance)
