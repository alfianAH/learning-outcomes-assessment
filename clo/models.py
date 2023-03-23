from django.db import models
from django.db.models import Q, CheckConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from learning_outcomes_assessment.utils import get_reverse_url
from lock_model.models import LockableMixin
from pi_area.models import PerformanceIndicator
from ilo.models import Ilo
from learning_outcomes_assessment.model_manager.models import TextNumberModelManager
from mata_kuliah_semester.models import (
    MataKuliahSemester,
    PesertaMataKuliah
)


# Create your models here.
class Clo(LockableMixin, models.Model):
    objects = TextNumberModelManager()
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255, null=False, blank=False)
    deskripsi = models.TextField(null=False)
    
    @property
    def get_kwargs(self):
        return {
            **self.mk_semester.get_kwargs,
            'clo_id': self.pk
        }

    def read_detail_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:read', self.get_kwargs)
    
    def get_clo_update_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:update', self.get_kwargs)
    
    # PI CLO and ILO
    def get_pi_clo(self):
        return self.piclo_set.all()
    
    def get_ilo(self):
        pi_clo = self.piclo_set.first()
        if pi_clo is None: return None

        pi_obj: PerformanceIndicator = pi_clo.performance_indicator
        ilo_obj: Ilo = pi_obj.pi_area.ilo
        return ilo_obj
    
    # Komponen CLO
    def get_komponen_clo(self):
        return self.komponenclo_set.all()
    
    def get_total_persentase_komponen(self):
        list_komponen_clo = self.get_komponen_clo()
        total_persentase = 0

        for komponen_clo in list_komponen_clo:
            total_persentase += komponen_clo.persentase

        return total_persentase
    
    def get_komponen_clo_bulk_delete_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:komponen-clo-bulk-delete', self.get_kwargs)
    
    def get_komponen_clo_create_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:komponen-clo-create', self.get_kwargs)
    
    def get_komponen_clo_graph_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:komponen-clo-graph', self.get_kwargs)


class KomponenClo(LockableMixin, models.Model):
    clo = models.ForeignKey(Clo, on_delete=models.CASCADE)

    teknik_penilaian = models.CharField(null=False, blank=False, max_length=255)
    instrumen_penilaian = models.CharField(null=False, blank=False, max_length=255)
    persentase = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        ordering = ['clo__nama', 'instrumen_penilaian']

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(persentase__gte=0.0) & Q(persentase__lte=100.0),
                name='persentase_range'
            ),
        )


class PiClo(LockableMixin, models.Model):
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
                name='nilai_komponen_clo_range'
            ),
        )


class NilaiCloPeserta(models.Model):
    peserta = models.ForeignKey(PesertaMataKuliah, on_delete=models.CASCADE)
    clo = models.ForeignKey(Clo, on_delete=models.CASCADE)

    nilai = models.FloatField(null=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        ordering = ['clo__nama']
        constraints = (
            CheckConstraint(
                check=Q(nilai__gte=0.0) & Q(nilai__lte=100.0),
                name='nilai_clo_peserta_range'
            ),
        )


class NilaiCloMataKuliahSemester(models.Model):
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)
    clo = models.ForeignKey(Clo, on_delete=models.CASCADE)

    nilai = models.FloatField(null=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        ordering = ['clo__nama']
        constraints = (
            CheckConstraint(
                check=Q(nilai__gte=0.0) & Q(nilai__lte=100.0),
                name='nilai_clo_mk_semester_range'
            ),
        )
