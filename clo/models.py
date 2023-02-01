from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from pi_area.models import PerformanceIndicator
from ilo.models import Ilo
from mata_kuliah_semester.models import (
    MataKuliahSemester,
    PesertaMataKuliah
)


# Create your models here.
class Clo(models.Model):
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255, null=False, blank=False)
    deskripsi = models.TextField(null=False)

    def get_pi_clo(self):
        return self.piclo_set.all()
    
    def get_ilo(self):
        list_pi_clo = self.get_pi_clo()
        if not list_pi_clo.exists(): return None

        pi_obj: PerformanceIndicator = list_pi_clo[0].performance_indicator
        ilo_obj: Ilo = pi_obj.pi_area.ilo
        return ilo_obj
    
    def get_komponen_clo(self):
        return self.komponenclo_set.all()
    
    def get_total_persentase_komponen(self):
        list_komponen_clo = self.get_komponen_clo()
        total_persentase = 0

        for komponen_clo in list_komponen_clo:
            total_persentase += komponen_clo.persentase

        return total_persentase


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
