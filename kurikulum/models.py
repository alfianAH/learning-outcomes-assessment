from django.db import models
from django.urls import reverse

from accounts.models import ProgramStudi


# Create your models here.
class Kurikulum(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255, null=False)
    tahun_mulai = models.IntegerField(null=False)
    total_sks_lulus = models.PositiveSmallIntegerField(null=True)
    is_active = models.BooleanField(null=False)

    def read_sync_url(self):
        return reverse('kurikulum:read-sync', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def read_detail_url(self):
        return reverse('kurikulum:read', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def delete_kurikulum_url(self):
        return reverse('kurikulum:delete', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def read_all_mata_kuliah_kurikulum_url(self):
        return reverse('kurikulum:mk-read-all', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_mata_kuliah_kurikulum(self):
        return self.matakuliahkurikulum_set.all()

    def get_semester(self):
        print('Semester: {}'.format(self.semesterkurikulum_set.all()))
        list_semester_kurikulum_obj = self.semesterkurikulum_set.all()
        list_semester = []
        for semester_kurikulum_obj in list_semester_kurikulum_obj:
            list_semester.append(semester_kurikulum_obj.semester)
        
        return list_semester


class MataKuliahKurikulum(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    kurikulum = models.ForeignKey(Kurikulum, on_delete=models.CASCADE)
    
    kode = models.CharField(max_length=100, null=False)
    nama = models.CharField(max_length=255, null=False)
    sks = models.PositiveSmallIntegerField(null=False)

    def __str__(self) -> str:
        return self.nama
