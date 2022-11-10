from django.db import models
from django.urls import reverse

from accounts.models import ProgramStudi


# Create your models here.
class Kurikulum(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255, null=False)
    tahun_mulai = models.IntegerField(null=False)
    tahun_akhir = models.IntegerField(null=False)
    total_sks_lulus = models.PositiveSmallIntegerField(null=False)
    is_active = models.BooleanField(null=False)

    def read_sync_url(self):
        return reverse('kurikulum:read-sync', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def read_kurikulum_url(self):
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


class MataKuliahKurikulum(models.Model):
    id_neosia = models.BigIntegerField(primary_key=True, null=False, unique=True)
    prodi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    kurikulum = models.ForeignKey(Kurikulum, on_delete=models.CASCADE)
    
    kode = models.CharField(max_length=100, null=False)
    nama = models.CharField(max_length=255, null=False)
    sks = models.PositiveSmallIntegerField(null=False)