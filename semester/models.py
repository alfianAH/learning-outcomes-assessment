from django.db import models

from kurikulum.models import Kurikulum
from .utils import extract_tahun_ajaran

# Create your models here.
class TipeSemester(models.TextChoices):
    GANJIL = 1, 'Ganjil'
    GENAP = 2, 'Genap'


class TahunAjaranManager(models.Manager):
    def get_or_create_tahun_ajaran(self, tahun_ajaran: str):
        extracted_tahun_ajaran = extract_tahun_ajaran(tahun_ajaran)
        filter_obj = self.get_or_create(**extracted_tahun_ajaran)
        return filter_obj


class TahunAjaran(models.Model):
    objects = TahunAjaranManager()
    
    tahun_ajaran_awal = models.IntegerField(null=False)
    tahun_ajaran_akhir = models.IntegerField(null=False)

    def __str__(self) -> str:
        return '{}/{}'.format(self.tahun_ajaran_awal, self.tahun_ajaran_akhir)


class Semester(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    
    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE)
    
    nama = models.CharField(max_length=255, null=False)
    tipe_semester = models.PositiveSmallIntegerField(choices=TipeSemester.choices, null=False)

    def __str__(self) -> str:
        return self.nama


class SemesterKurikulum(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    kurikulum = models.ForeignKey(Kurikulum, on_delete=models.CASCADE)
