from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserOAuthManager

# Create your models here.
class MyUser(AbstractUser):
    objects = UserOAuthManager()

    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    prodi = models.CharField(max_length=50)
    fakultas = models.CharField(max_length=20)
