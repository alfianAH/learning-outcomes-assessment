from django.db import models


class RoleChoices(models.TextChoices):
    ADMIN_PRODI = 'a', 'Admin Program Studi'
    DOSEN = 'd', 'Dosen'
    MAHASISWA = 'm', 'Mahasiswa'
