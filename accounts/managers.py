from django.contrib.auth import models

from .enums import RoleChoices

class UserOAuthManager(models.UserManager):
    def create_admin_prodi_user(self, user):
        new_user = self.create(
            username = user["nip"],
            name = user["nama_admin"],
            prodi = user["nama_prodi"],
            fakultas = user["nama_fakultas"],
            role=RoleChoices.ADMIN_PRODI
        )

        return new_user

    def create_dosen_user(self, user):
        new_user = self.create(
            username = user["nip"],
            name = user["nama_dosen"],
            prodi = user["nama_prodi"],
            fakultas = user["nama_fakultas"],
            role=RoleChoices.DOSEN
        )

        return new_user
    
    def create_mahasiswa_user(self, user):
        new_user = self.create(
            username = user["nim"],
            name = user["nama_mahasiswa"],
            prodi = user["nama_prodi"],
            fakultas = user["nama_fakultas"],
            role=RoleChoices.MAHASISWA
        )

        return new_user