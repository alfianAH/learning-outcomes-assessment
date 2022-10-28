from django.contrib.auth import models
from django.contrib.auth.models import Group

from .enums import RoleChoices

class UserOAuthManager(models.UserManager):
    def create_admin_prodi_user(self, user: dict, prodi):
        admin_prodi_group, _ = Group.objects.get_or_create(name='Admin Program Studi')
        new_user = self.create_user(
            user['nip'],
            user['nama_admin'],
            RoleChoices.ADMIN_PRODI,
            prodi
        )

        new_user.groups.add(admin_prodi_group)
        return new_user

    def create_dosen_user(self, user: dict, prodi):
        dosen_group, _ = Group.objects.get_or_create(name='Dosen')
        new_user = self.create_user(
            user['nip'],
            user['nama_dosen'],
            RoleChoices.DOSEN,
            prodi
        )

        new_user.groups.add(dosen_group)
        return new_user
    
    def create_mahasiswa_user(self, user: dict, prodi):
        mahasiswa_group, _ = Group.objects.get_or_create(name='Mahasiswa')
        new_user = self.create_user(
            user['nim'],
            user['nama_mahasiswa'],
            RoleChoices.MAHASISWA,
            prodi
        )

        new_user.groups.add(mahasiswa_group)
        return new_user
    
    def create_user(self, username: str, name: str, role: str, prodi):
        new_user = self.create(
            username = username,
            name = name,
            prodi = prodi,
            role = role,
        )
        
        return new_user
