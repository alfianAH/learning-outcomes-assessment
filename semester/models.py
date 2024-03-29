from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts.models import ProgramStudiJenjang
from learning_outcomes_assessment.utils import (
    extract_tahun_ajaran,
    get_reverse_url
)

# Create your models here.
class TipeSemester(models.IntegerChoices):
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

    class Meta:
        ordering = ('tahun_ajaran_awal', 'tahun_ajaran_akhir')

    def __str__(self) -> str:
        return '{}/{}'.format(self.tahun_ajaran_awal, self.tahun_ajaran_akhir)


class TahunAjaranProdi(models.Model):
    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE)
    prodi_jenjang = models.ForeignKey(ProgramStudiJenjang, on_delete=models.CASCADE)


class Semester(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    
    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE)
    
    nama = models.CharField(max_length=255, null=False)
    tipe_semester = models.PositiveSmallIntegerField(choices=TipeSemester.choices, null=False)

    def __str__(self) -> str:
        return self.nama


class SemesterProdi(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    tahun_ajaran_prodi = models.ForeignKey(TahunAjaranProdi, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    @property
    def get_kwargs(self):
        return {
            'semester_prodi_id': self.pk
        }

    def get_mk_semester(self):
        return self.matakuliahsemester_set.all()

    def read_detail_url(self):
        return get_reverse_url('semester:read', self.get_kwargs)

    # Mata kuliah semester
    def read_all_mk_semester_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:read-all', self.get_kwargs)

    def get_create_mk_semester_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:create', self.get_kwargs)

    def get_bulk_delete_mk_semester_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:bulk-delete', self.get_kwargs)
