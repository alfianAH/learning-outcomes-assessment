from django.db import models
from django.contrib.auth.models import AbstractUser, Group, UserManager
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


class UserOAuthManager(UserManager):
    def create_admin_prodi_user(self, user: dict, prodi: ProgramStudi):
        admin_prodi_group, _ = Group.objects.get_or_create(name='Admin Program Studi')
        new_user = self.create_user(
            user['nip'],
            user['nama_admin'],
            RoleChoices.ADMIN_PRODI,
            prodi
        )

        new_user.groups.add(admin_prodi_group)
        return new_user

    def create_dosen_user(self, user: dict, prodi: ProgramStudi):
        dosen_group, _ = Group.objects.get_or_create(name='Dosen')
        new_user = self.create_user(
            user['nip'],
            user['nama_dosen'],
            RoleChoices.DOSEN,
            prodi
        )

        new_user.groups.add(dosen_group)
        return new_user
    
    def create_mahasiswa_user(self, user: dict, prodi: ProgramStudi):
        mahasiswa_group, _ = Group.objects.get_or_create(name='Mahasiswa')
        new_user = self.create_user(
            user['nim'],
            user['nama_mahasiswa'],
            RoleChoices.MAHASISWA,
            prodi
        )

        new_user.groups.add(mahasiswa_group)
        return new_user
    
    def create_user(self, username: str, name: str, role: str, prodi: ProgramStudi):
        new_user = self.create(
            username = username,
            name = name,
            prodi = prodi,
            role = role,
        )
        
        return new_user


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
