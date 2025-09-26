from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser
    to support Google OAuth authentication and additional profile fields.
    """
    # Google OAuth fields
    google_id = models.CharField(max_length=100, unique=True, null=True, blank=True, 
                                help_text="Google account ID from OAuth")
    avatar_url = models.URLField(max_length=500, null=True, blank=True,
                                help_text="Profile picture URL from Google")
    
    # Additional profile fields
    is_email_verified = models.BooleanField(default=False,
                                           help_text="Whether the email has been verified")
    created_at = models.DateTimeField(default=timezone.now,
                                     help_text="When the user was created")
    updated_at = models.DateTimeField(auto_now=True,
                                     help_text="When the user was last updated")
    
    # Subscription/Premium features (for future lootbox system)
    is_premium = models.BooleanField(default=False,
                                   help_text="Whether user has premium subscription")
    subscription_tier = models.CharField(max_length=20, 
                                       choices=[
                                           ('basic', 'Basic'),
                                           ('premium', 'Premium'),
                                           ('elite', 'Elite'),
                                       ],
                                       default='basic')
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
