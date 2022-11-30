from django.db import models

from accounts.models import ProgramStudi
from kurikulum.models import Kurikulum

# Create your models here.
class MataKuliahKurikulum(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    kurikulum = models.ForeignKey(Kurikulum, on_delete=models.CASCADE)
    
    kode = models.CharField(max_length=100, null=False)
    nama = models.CharField(max_length=255, null=False)
    sks = models.PositiveSmallIntegerField(null=False)

    def __str__(self) -> str:
        return self.nama
