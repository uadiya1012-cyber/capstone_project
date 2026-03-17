from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MODERATOR', 'Moderator'),
        ('USER', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        # Hide role in string representation to avoid showing it in logs/UI
        return f"{self.username}"