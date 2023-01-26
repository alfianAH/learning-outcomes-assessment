from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from pi_area.models import PerformanceIndicator
from mata_kuliah_semester.models import (
    MataKuliahSemester,
    PesertaMataKuliah
)


# Create your models here.
class Clo(models.Model):
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255, null=False, blank=False)
    deskripsi = models.TextField(null=False)


class KomponenClo(models.Model):
    clo = models.ForeignKey(Clo, on_delete=models.CASCADE)

    teknik_penilaian = models.CharField(null=False, blank=False, max_length=255)
    instrumen_penilaian = models.CharField(null=False, blank=False, max_length=255)
    persentase = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(persentase__gte=0.0) & Q(persentase__lte=100.0),
                name='persentase_range'
            ),
        )


class PiClo(models.Model):
    performance_indicator = models.ForeignKey(PerformanceIndicator, on_delete=models.CASCADE)
    clo = models.ForeignKey(Clo, on_delete=models.CASCADE)


class NilaiKomponenCloPeserta(models.Model):
    komponen_clo = models.ForeignKey(KomponenClo, on_delete=models.CASCADE)
    peserta = models.ForeignKey(PesertaMataKuliah, on_delete=models.CASCADE)

    nilai = models.FloatField(null=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(nilai__gte=0.0) & Q(nilai__lte=100.0),
                name='nilai_range'
            ),
        )
