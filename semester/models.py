from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from kurikulum.models import Kurikulum
from learning_outcomes_assessment.utils import extract_tahun_ajaran

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

    def read_detail_url(self):
        return reverse('semester:read', kwargs={
            'semester_kurikulum_id': self.pk
        })

    # Performance Indicator Area
    def read_all_pi_area_url(self):
        return reverse('semester:pi_area:read-all', kwargs={
            'semester_kurikulum_id': self.pk
        })

    def get_hx_create_pi_area_url(self):
        return reverse('semester:pi_area:hx-create', kwargs={
            'semester_kurikulum_id': self.pk
        })

    def get_create_pi_area_url(self):
        return reverse('semester:pi_area:create', kwargs={
            'semester_kurikulum_id': self.pk
        })

    def get_bulk_delete_pi_area_url(self):
        return reverse('semester:pi_area:pi-area-bulk-delete', kwargs={
            'semester_kurikulum_id': self.pk
        })

    # ILO
    def read_all_ilo_url(self):
        return reverse('semester:ilo:read-all', kwargs={
            'semester_kurikulum_id': self.pk
        })

    def get_hx_create_ilo_url(self):
        return reverse('semester:ilo:hx-create', kwargs={
            'semester_kurikulum_id': self.pk
        })

    def get_create_ilo_url(self):
        return reverse('semester:ilo:create', kwargs={
            'semester_kurikulum_id': self.pk
        })

    def get_ilo_bulk_delete_url(self):
        return reverse('semester:ilo:bulk-delete', kwargs={
            'semester_kurikulum_id': self.pk
        })
