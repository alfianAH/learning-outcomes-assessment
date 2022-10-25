from django.contrib.auth import models

class UserOAuthManager(models.UserManager):
    def create_new_user(self, user):
        new_user = self.create(
            username = user["nim"],
            name = user["nama_mahasiswa"],
            prodi = user["nama_prodi"],
            fakultas = user["nama_fakultas"],
        )

        return new_user