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

    def __str__(self) -> str:
        return self.nama

    def read_sync_url(self):
        return reverse('kurikulum:read-sync', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def read_detail_url(self):
        return reverse('kurikulum:read', kwargs={
            'kurikulum_id': self.id_neosia
        })

    # Mata Kuliah Kurikulum
    def get_mk_kurikulum(self):
        return self.matakuliahkurikulum_set.all()

    def get_mk_bulk_delete(self):
        return reverse('kurikulum:mk-bulk-delete', kwargs={
            'kurikulum_id': self.id_neosia
        })
    
    def get_mk_create(self):
        return reverse('kurikulum:mk-create', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_mk_update(self):
        return reverse('kurikulum:mk-update', kwargs={
            'kurikulum_id': self.id_neosia
        })
