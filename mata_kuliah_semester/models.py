from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.conf import settings
from ilo.models import Ilo
from mata_kuliah_kurikulum.models import MataKuliahKurikulum
from semester.models import SemesterProdi

User = settings.AUTH_USER_MODEL

# Create your models here.
class MataKuliahSemester(models.Model):
    mk_kurikulum = models.ForeignKey(MataKuliahKurikulum, on_delete=models.CASCADE)
    semester = models.ForeignKey(SemesterProdi, on_delete=models.CASCADE)

    average_clo_achievement = models.FloatField(null=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(average_clo_achievement__gte=0.0) & Q(average_clo_achievement__lte=100.0),
                name='average_clo_achievement_range'
            ),
        )

    def read_detail_url(self):
        return reverse('semester:mata_kuliah_semester:read', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })


class KelasMataKuliahSemester(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255)
    kelas = models.CharField(max_length=255)


class PesertaMataKuliah(models.Model):
    kelas_mk_semester = models.ForeignKey(KelasMataKuliahSemester, on_delete=models.CASCADE)
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE)


class DosenMataKuliah(models.Model):
    kelas_mk_semester = models.ForeignKey(KelasMataKuliahSemester, on_delete=models.CASCADE)
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE)


class NilaiMataKuliahMahasiswa(models.Model):
    peserta = models.ForeignKey(PesertaMataKuliah, on_delete=models.CASCADE)
    nilai_akhir = models.FloatField(null=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(nilai_akhir__gte=0.0) & Q(nilai_akhir__lte=100.0),
                name='nilai_akhir_range'
            ),
        ) 


class NilaiMataKuliahIloMahasiswa(models.Model):
    peserta = models.ForeignKey(PesertaMataKuliah, on_delete=models.CASCADE)
    ilo = models.ForeignKey(Ilo, on_delete=models.CASCADE)
    nilai_ilo = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(nilai_ilo__gte=0.0) & Q(nilai_ilo__lte=100.0),
                name='nilai_ilo_range'
            ),
        ) 
