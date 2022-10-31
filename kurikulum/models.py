from enum import unique
from django.db import models

from accounts.models import ProgramStudi


# Create your models here.
class Kurikulum(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255, null=False)
    tahun_mulai = models.IntegerField(null=False)
    tahun_akhir = models.IntegerField(null=False)
    total_sks_lulus = models.IntegerField(null=False)
    is_active = models.BooleanField(null=False)
