from django.db import models
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.urls import reverse
from .enums import RoleChoices


# Create your models here.
class Fakultas(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    nama = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.nama


class ProgramStudi(models.Model):
    fakultas = models.ForeignKey(Fakultas, on_delete=models.CASCADE, null=True)
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    nama = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.nama

    def get_prodi_jenjang(self):
        return self.programstudijenjang_set.all()

    def get_prodi_read_url(self):
        return reverse('accounts:prodi-read', kwargs={
            'prodi_id': self.id_neosia
        })

    def get_prodi_bulk_update_url(self):
        return reverse('accounts:prodi-bulk-update', kwargs={
            'prodi_id': self.id_neosia
        })

    def get_prodi_bulk_update_sks_url(self):
        return reverse('accounts:prodi-bulk-update-sks', kwargs={
            'prodi_id': self.id_neosia
        })

    def get_prodi_create_url(self):
        return reverse('accounts:prodi-create', kwargs={
            'prodi_id': self.id_neosia
        })

    def get_bulk_delete_prodi_jenjang_url(self):
        return reverse('accounts:prodi-jenjang-bulk-delete', kwargs={
            'prodi_id': self.id_neosia
        })


class JenjangStudi(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    nama = models.CharField(max_length=255)
    kode = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.nama


class ProgramStudiJenjang(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    program_studi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    jenjang_studi = models.ForeignKey(JenjangStudi, on_delete=models.CASCADE)
    
    nama = models.CharField(max_length=255)
    total_sks_lulus = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['jenjang_studi__id_neosia']


class UserOAuthManager(UserManager):
    def create_admin_prodi_user(self, user: dict, prodi: ProgramStudi):
        admin_prodi_group, _ = Group.objects.get_or_create(name='Admin Program Studi')
        new_user = self.create_user(
            user['username'],
            user['nama'],
            RoleChoices.ADMIN_PRODI,
            prodi
        )

        new_user.groups.add(admin_prodi_group)
        return new_user

    def create_dosen_user(self, user: dict, prodi: ProgramStudi):
        dosen_group, _ = Group.objects.get_or_create(name='Dosen')
        new_user = self.create_user(
            user['username'],
            user['nama'],
            RoleChoices.DOSEN,
            prodi
        )

        new_user.groups.add(dosen_group)
        return new_user
    
    def create_mahasiswa_user(self, user: dict, prodi: ProgramStudi):
        mahasiswa_group, _ = Group.objects.get_or_create(name='Mahasiswa')
        if user.get('nama_mahasiswa') is not None:
            new_user = self.create_user(
                user['nim'],
                user['nama_mahasiswa'],
                RoleChoices.MAHASISWA,
                prodi
            )
        else:
            new_user = self.create_user(
                user['nim'],
                user['nama'],
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
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    role = models.CharField(max_length=1, choices=RoleChoices.choices, null=False)

    def __str__(self) -> str:
        return self.username
