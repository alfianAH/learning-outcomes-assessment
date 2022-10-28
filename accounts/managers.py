from django.contrib.auth import models

from .enums import RoleChoices

class UserOAuthManager(models.UserManager):
    def create_admin_prodi_user(self, user: dict, prodi):
        new_user = self.create_user(
            user['nip'],
            user['nama_admin'],
            RoleChoices.ADMIN_PRODI,
            prodi
        )

        return new_user

    def create_dosen_user(self, user: dict, prodi):
        new_user = self.create_user(
            user['nip'],
            user['nama_dosen'],
            RoleChoices.DOSEN,
            prodi
        )

        return new_user
    
    def create_mahasiswa_user(self, user: dict, prodi):
        new_user = self.create_user(
            user['nim'],
            user['nama_mahasiswa'],
            RoleChoices.MAHASISWA,
            prodi
        )

        return new_user
    
    def create_user(self, username: str, name: str, role: str, prodi):
        new_user = self.create(
            username = username,
            name = name,
            prodi = prodi,
            role = role,
        )
        
        return new_user
