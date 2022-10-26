from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserOAuthManager
from .enums import RoleChoices

# Create your models here.
class MyUser(AbstractUser):
    objects = UserOAuthManager()

    username = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=100, null=False)
    role = models.CharField(max_length=1, choices=RoleChoices.choices, null=False)
    prodi = models.CharField(max_length=50, null=False)
    fakultas = models.CharField(max_length=20, null=False)
