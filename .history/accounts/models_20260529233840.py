from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_journalist = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
