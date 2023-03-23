from django.db import models
from django.conf import settings
from django.db.models import Q, CheckConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from mata_kuliah_semester.models import MataKuliahSemester
from clo.models import Clo


User = settings.AUTH_USER_MODEL

# Create your models here.
class RencanaPembelajaranSemester(models.Model):
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)
    kaprodi = models.ForeignKey(User, on_delete=models.CASCADE)

    semester = models.PositiveSmallIntegerField(null=False, blank=False)
    deskripsi = models.TextField(null=False, blank=False)
    clo_details = models.TextField(null=False, blank=False)
    materi_pembelajaran = models.TextField(null=False, blank=False)
    pustaka_utama = models.TextField(null=True, blank=True)
    pustaka_pendukung = models.TextField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)


class PengembangRPS(models.Model):
    rps = models.ForeignKey(RencanaPembelajaranSemester, on_delete=models.CASCADE)
    dosen = models.ForeignKey(User, on_delete=models.CASCADE)


class KoordinatorRPS(models.Model):
    rps = models.ForeignKey(RencanaPembelajaranSemester, on_delete=models.CASCADE)
    dosen = models.ForeignKey(User, on_delete=models.CASCADE)


class DosenPengampuRPS(models.Model):
    rps = models.ForeignKey(RencanaPembelajaranSemester, on_delete=models.CASCADE)
    dosen = models.ForeignKey(User, on_delete=models.CASCADE)


class MataKuliahSyaratRPS(models.Model):
    rps = models.ForeignKey(RencanaPembelajaranSemester, on_delete=models.CASCADE)
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)


class PertemuanRPS(models.Model):
    rps = models.ForeignKey(RencanaPembelajaranSemester, on_delete=models.CASCADE)
    clo = models.ForeignKey(Clo, on_delete=models.CASCADE)
    
    pertemuan_awal = models.PositiveSmallIntegerField(null=False, blank=False)
    pertemuan_akhir = models.PositiveSmallIntegerField(null=True, blank=True)
    learning_outcome = models.TextField(null=False, blank=False)

    # Penilaian
    indikator = models.TextField(null=False, blank=False)
    bentuk_kriteria = models.TextField(null=False, blank=False)

    materi_pembelajaran = models.TextField(null=False, blank=False)
    bobot_penilaian = models.SmallIntegerField(null=False, blank=False, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(bobot_penilaian__gte=0.0) & Q(bobot_penilaian__lte=100.0),
                name='bobot_penilaian_pertemuan_rps_range'
            ),
        )


class PembelajaranPertemuanRPS(models.Model):
    pertemuan_rps = models.OneToOneField(PertemuanRPS, on_delete=models.CASCADE)

    bentuk_pembelajaran = models.TextField(null=False, blank=False)
    metode_pembelajaran = models.TextField(null=False, blank=False)


class DurasiPertemuanRPS(models.Model):
    pertemuan_rps = models.OneToOneField(PertemuanRPS, on_delete=models.CASCADE)

    tipe_durasi = models.CharField(max_length=255, null=False, blank=False)
    pengali_durasi = models.SmallIntegerField(null=False, blank=False)
    durasi_menit = models.SmallIntegerField(null=False, blank=False, validators=[MinValueValidator(0.0), MaxValueValidator(60.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(durasi_menit__gte=0.0) & Q(durasi_menit__lte=60.0),
                name='durasi_menit_pertemuan_rps_range'
            ),
        )