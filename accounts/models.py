from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserOAuthManager
from .enums import RoleChoices

# Create your models here.
class Fakultas(models.Model):
    id_neosia = models.IntegerField(unique=True, null=False, primary_key=True)
    nama = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.nama

class ProgramStudi(models.Model):
    fakultas = models.ForeignKey(Fakultas, on_delete=models.CASCADE)
    id_neosia = models.IntegerField(unique=True, null=False, primary_key=True)
    nama = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.nama

class MyUser(AbstractUser):
    # Unused default fields
    email = None
    first_name = None
    last_name = None
    password = None
    
    objects = UserOAuthManager()
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=100, null=False)
    role = models.CharField(max_length=1, choices=RoleChoices.choices, null=False)

    def __str__(self) -> str:
        return self.username
