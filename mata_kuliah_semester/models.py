from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from learning_outcomes_assessment.utils import get_reverse_url
from ilo.models import Ilo
from mata_kuliah_kurikulum.models import MataKuliahKurikulum
from semester.models import SemesterProdi
from learning_outcomes_assessment.utils import nilai_excel_upload_handler

User = settings.AUTH_USER_MODEL

# Create your models here.
class MataKuliahSemesterLock(models.Model):
    is_clo_locked = models.BooleanField(default=False)
    is_rps_locked = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class MataKuliahSemester(MataKuliahSemesterLock):
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
    
    @property
    def get_kwargs(self):
        return {
            **self.semester.get_kwargs,
            'mk_semester_id': self.pk,
        }
    
    # Pedoman
    @property
    def status_pedoman(self):
        return self.is_clo_locked and self.is_rps_locked

    def read_detail_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:read', self.get_kwargs)
    
    # Kelas MK Semester
    def get_kelas_mk_semester(self):
        return self.kelasmatakuliahsemester_set.all()
    
    def get_kelas_mk_semester_update_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:kelas-mk-semester-bulk-update', self.get_kwargs)
    
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
    
    @property
    def status_nilai(self) -> bool:
        """Status nilai all peserta in MK Semester

        Returns:
            bool: Returns True if all nilai peserta are complete, else returns False. Returns False if MK Semester has no peserta. 
        """
        
        list_peserta_mk = self.get_all_peserta_mk_semester()
        if len(list_peserta_mk) == 0:
            return False
        return all(peserta.status_nilai for peserta in list_peserta_mk)
    
    def get_peserta_mk_semester_create_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:peserta-create', self.get_kwargs)
    
    def get_peserta_mk_semester_bulk_delete_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:peserta-bulk-delete', self.get_kwargs)
    
    def get_peserta_mk_semester_bulk_update_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:peserta-bulk-update', self.get_kwargs)
    
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
        return get_reverse_url('semester:mata_kuliah_semester:clo:read-all', self.get_kwargs)
    
    def get_clo_read_all_graph_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:read-all-graph', self.get_kwargs)
    
    def get_clo_create_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:create', self.get_kwargs)
    
    def get_clo_bulk_delete_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:bulk-delete', self.get_kwargs)
    
    def get_clo_duplicate_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:duplicate', self.get_kwargs)
    
    def get_clo_lock_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:lock', self.get_kwargs)
    
    def get_clo_unlock_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:clo:unlock', self.get_kwargs)
    
    # Nilai Komponen CLO Peserta
    def get_nilai_komponen_edit_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:nilai-komponen-edit', self.get_kwargs)
    
    def get_hx_nilai_komponen_import_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:hx-nilai-komponen-import', self.get_kwargs)
    
    def get_nilai_komponen_import_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:nilai-komponen-import', self.get_kwargs)
    
    # Nilai Average CLO Achivement
    def get_nilai_clo_mk_semester(self):
        return self.nilaiclomatakuliahsemester_set.all()
    
    def get_nilai_average_calculate_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:nilai-avg-calculate', self.get_kwargs)
    
    # RPS
    @property
    def status_rincian(self):
        if not hasattr(self, 'rencanapembelajaransemester'): 
            status = False
        else:
            status = True
        return status

    def get_syarat_mata_kuliah_rps(self):
        return self.matakuliahsyaratrps_set.all()
    
    def get_rps_home_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:home', self.get_kwargs)
    
    def get_rps_create_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:create', self.get_kwargs)
    
    def get_rps_update_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:update', self.get_kwargs)
    
    def get_rps_delete_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:delete', self.get_kwargs)
    
    def get_rps_duplicate_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:duplicate', self.get_kwargs)
    
    # Pertemuan RPS
    def get_all_pertemuan_rps(self):
        return self.pertemuanrps_set.all()
    
    @property
    def get_total_bobot_penilaian_pertemuan_rps(self):
        list_pertemuan_rps = self.get_all_pertemuan_rps()
        total_bobot_penilaian = 0

        for pertemuan_rps in list_pertemuan_rps:
            total_bobot_penilaian += pertemuan_rps.bobot_penilaian
        
        return total_bobot_penilaian
    
    @property
    def status_pertemuan(self):
        if not hasattr(self, 'pertemuanrps_set'): 
            status = False
        else:
            status = True
        return status
    
    def get_pertemuan_rps_create_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:pertemuan-create', self.get_kwargs)
    
    def get_pertemuan_rps_bulk_delete_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:pertemuan-bulk-delete', self.get_kwargs)
    
    def get_pertemuan_rps_duplicate_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:rps:pertemuan-duplicate', self.get_kwargs)
    

class NilaiExcelMataKuliahSemester(models.Model):
    mk_semester = models.OneToOneField(MataKuliahSemester, on_delete=models.CASCADE)
    file = models.FileField(null=True, upload_to=nilai_excel_upload_handler)
    created_at = models.DateTimeField(auto_now_add=True)
    

class KelasMataKuliahSemester(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    mk_semester = models.ForeignKey(MataKuliahSemester, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255)

    class Meta:
        ordering = ['nama',]

    def __str__(self) -> str:
        return self.nama
    
    @property
    def get_kwargs(self):
        return {
            **self.mk_semester.get_kwargs,
            'kelas_mk_semester_id': self.pk
        }

    def get_dosen_mata_kuliah(self):
        return self.dosenmatakuliah_set.all()
    
    def get_peserta_mata_kuliah(self):
        return self.pesertamatakuliah_set.all()
    
    def get_delete_kelas_mk_semester_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:kelas-mk-semester-delete', self.get_kwargs)


class PesertaMataKuliah(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    kelas_mk_semester = models.ForeignKey(KelasMataKuliahSemester, on_delete=models.CASCADE)
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE)
    nilai_akhir = models.FloatField(null=True, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    nilai_huruf = models.CharField(null=True, max_length=5)
    status_nilai = models.BooleanField(default=False)
    
    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(nilai_akhir__gte=0.0) & Q(nilai_akhir__lte=100.0),
                name='nilai_akhir_range'
            ),
        )
    
    @property
    def get_kwargs(self):
        return {
            **self.kelas_mk_semester.mk_semester.get_kwargs,
            'peserta_id': self.pk
        }

    def get_student_performance_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:student-performance', self.get_kwargs)
    
    def get_calculate_student_performance_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:calculate-student-performance', self.get_kwargs)

    # Komponen CLO
    def get_all_nilai_komponen_clo_peserta(self):
        return self.nilaikomponenclopeserta_set.filter(
            komponen_clo__clo__in=self.kelas_mk_semester.mk_semester.get_all_clo()
        )
    
    def get_nilai_komponen_clo_peserta(self, komponen_clo):
        return self.nilaikomponenclopeserta_set.filter(
            komponen_clo=komponen_clo
        )
    
    def get_hx_nilai_komponen_clo_peserta_edit_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:hx-nilai-komponen-peserta-edit', self.get_kwargs)
    
    def get_nilai_komponen_clo_peserta_edit_url(self):
        return get_reverse_url('semester:mata_kuliah_semester:nilai-komponen-peserta-edit', self.get_kwargs)
    
    # Nilai ILO
    def get_nilai_ilo(self):
        return self.nilaimatakuliahilomahasiswa_set.all()


class DosenMataKuliah(models.Model):
    kelas_mk_semester = models.ForeignKey(KelasMataKuliahSemester, on_delete=models.CASCADE)
    dosen = models.ForeignKey(User, on_delete=models.CASCADE)


class NilaiMataKuliahIloMahasiswa(models.Model):
    peserta = models.ForeignKey(PesertaMataKuliah, on_delete=models.CASCADE)
    ilo = models.ForeignKey(Ilo, on_delete=models.CASCADE)
    nilai_ilo = models.FloatField(null=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        ordering = ['ilo__nama']
        constraints = (
            CheckConstraint(
                check=Q(nilai_ilo__gte=0.0) & Q(nilai_ilo__lte=100.0),
                name='nilai_ilo_range'
            ),
        ) 
