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
    
    # Kelas MK Semester
    def get_kelas_mk_semester(self):
        return self.kelasmatakuliahsemester_set.all()
    
    def get_kelas_mk_semester_update_url(self):
        return reverse('semester:mata_kuliah_semester:kelas-mk-semester-bulk-update', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    # Dosen MK
    def get_all_dosen_mk_semester(self):
        list_user_dosen = []
        list_dosen = []
        list_kelas_mk_semester = self.get_kelas_mk_semester()

        for kelas_mk_semester in list_kelas_mk_semester:
            list_dosen_kelas_mk_semester = kelas_mk_semester.get_dosen_mata_kuliah()
            for dosen_kelas_mk_semester in list_dosen_kelas_mk_semester:
                if dosen_kelas_mk_semester.dosen.pk in list_user_dosen: continue
                list_dosen.append(dosen_kelas_mk_semester)
                list_user_dosen.append(dosen_kelas_mk_semester.dosen.pk)
        
        return list_dosen
    
    # Peserta MK
    def get_all_peserta_mk_semester(self):
        list_peserta = []
        list_kelas_mk_semester = self.get_kelas_mk_semester()

        for kelas_mk_semester in list_kelas_mk_semester:
            list_peserta_kelas_mk_semester = kelas_mk_semester.get_peserta_mata_kuliah()
            for peserta_kelas_mk_semester in list_peserta_kelas_mk_semester:
                list_peserta.append(peserta_kelas_mk_semester)
        
        return list_peserta
    
    def get_peserta_mk_semester_create_url(self):
        return reverse('semester:mata_kuliah_semester:peserta-create', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    def get_peserta_mk_semester_bulk_delete_url(self):
        return reverse('semester:mata_kuliah_semester:peserta-bulk-delete', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    def get_peserta_mk_semester_bulk_update_url(self):
        return reverse('semester:mata_kuliah_semester:peserta-bulk-update', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    # CLO
    def get_all_clo(self):
        return self.clo_set.all()
    
    def get_total_persentase_clo(self):
        list_clo = self.get_all_clo()
        total_persentase = 0

        for clo in list_clo:
            total_persentase += clo.get_total_persentase_komponen()
        
        return total_persentase
    
    def get_clo_read_all_url(self):
        return reverse('semester:mata_kuliah_semester:clo:read-all', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    def get_clo_read_all_graph_url(self):
        return reverse('semester:mata_kuliah_semester:clo:read-all-graph', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    def get_clo_create_url(self):
        return reverse('semester:mata_kuliah_semester:clo:create', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    def get_clo_bulk_delete_url(self):
        return reverse('semester:mata_kuliah_semester:clo:bulk-delete', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    def get_clo_duplicate_url(self):
        return reverse('semester:mata_kuliah_semester:clo:duplicate', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })
    
    # Nilai Komponen CLO Peserta
    def get_nilai_komponen_edit_url(self):
        return reverse('semester:mata_kuliah_semester:nilai-komponen-edit', kwargs={
            'semester_prodi_id': self.semester.pk,
            'mk_semester_id': self.pk
        })


class KelasMataKuliahSemester(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255)

    class Meta:
        ordering = ['nama',]

    def __str__(self) -> str:
        return self.nama

    def get_dosen_mata_kuliah(self):
        return self.dosenmatakuliah_set.all()
    
    def get_peserta_mata_kuliah(self):
        return self.pesertamatakuliah_set.all()
    
    def get_delete_kelas_mk_semester_url(self):
        return reverse('semester:mata_kuliah_semester:kelas-mk-semester-delete', kwargs={
            'semester_prodi_id': self.mk_semester.semester.pk,
            'mk_semester_id': self.mk_semester.pk,
            'kelas_mk_semester_id': self.id_neosia
        })


class PesertaMataKuliah(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    kelas_mk_semester = models.ForeignKey(KelasMataKuliahSemester, on_delete=models.CASCADE)
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE)
    nilai_akhir = models.FloatField(null=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    nilai_huruf = models.CharField(null=True, max_length=5)
    
    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(nilai_akhir__gte=0.0) & Q(nilai_akhir__lte=100.0),
                name='nilai_akhir_range'
            ),
        )
    
    def get_empty_komponen_clo(self):
        list_clo = self.kelas_mk_semester.mk_semester.get_all_clo()
        list_komponen_clo = []

        for clo in list_clo:
            for komponen_clo in clo.get_komponen_clo():
                list_komponen_clo.append(komponen_clo)
        
        return list_komponen_clo

    def get_nilai_komponen_clo_peserta(self):
        return self.nilaikomponenclopeserta_set.filter(
            komponen_clo__clo__in=self.kelas_mk_semester.mk_semester.get_all_clo()
        )
    
    def get_hx_nilai_komponen_clo_peserta_edit_url(self):
        return reverse('semester:mata_kuliah_semester:hx-nilai-komponen-peserta-edit', kwargs={
            'semester_prodi_id': self.kelas_mk_semester.mk_semester.semester.pk,
            'mk_semester_id': self.kelas_mk_semester.mk_semester.pk,
            'peserta_id': self.id_neosia,
        })
    
    def get_nilai_komponen_clo_peserta_edit_url(self):
        return reverse('semester:mata_kuliah_semester:nilai-komponen-peserta-edit', kwargs={
            'semester_prodi_id': self.kelas_mk_semester.mk_semester.semester.pk,
            'mk_semester_id': self.kelas_mk_semester.mk_semester.pk,
            'peserta_id': self.id_neosia,
        })


class DosenMataKuliah(models.Model):
    kelas_mk_semester = models.ForeignKey(KelasMataKuliahSemester, on_delete=models.CASCADE)
    dosen = models.ForeignKey(User, on_delete=models.CASCADE)


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
