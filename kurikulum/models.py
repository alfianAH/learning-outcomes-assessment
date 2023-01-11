from django.db import models
from django.urls import reverse

from accounts.models import ProgramStudiJenjang


# Create your models here.
class Kurikulum(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    prodi_jenjang = models.ForeignKey(ProgramStudiJenjang, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255, null=False)
    tahun_mulai = models.IntegerField(null=False)
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
    
    def read_all_mk_kurikulum_url(self):
        return reverse('kurikulum:mata_kuliah_kurikulum:read-all', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_bulk_delete_mk_kurikulum_url(self):
        return reverse('kurikulum:mata_kuliah_kurikulum:bulk-delete', kwargs={
            'kurikulum_id': self.id_neosia
        })
    
    def get_create_mk_kurikulum_url(self):
        return reverse('kurikulum:mata_kuliah_kurikulum:create', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_bulk_update_mk_kurikulum_url(self):
        return reverse('kurikulum:mata_kuliah_kurikulum:bulk-update', kwargs={
            'kurikulum_id': self.id_neosia
        })

    # Performance Indicator Area
    def read_all_pi_area_url(self):
        return reverse('kurikulum:pi_area:read-all', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_hx_create_pi_area_url(self):
        return reverse('kurikulum:pi_area:hx-create', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_create_pi_area_url(self):
        return reverse('kurikulum:pi_area:create', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_bulk_delete_pi_area_url(self):
        return reverse('kurikulum:pi_area:pi-area-bulk-delete', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_duplicate_pi_area_url(self):
        return reverse('kurikulum:pi_area:duplicate', kwargs={
            'kurikulum_id': self.id_neosia
        })

    # ILO
    def read_all_ilo_url(self):
        return reverse('kurikulum:ilo:read-all', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_hx_create_ilo_url(self):
        return reverse('kurikulum:ilo:hx-create', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_create_ilo_url(self):
        return reverse('kurikulum:ilo:create', kwargs={
            'kurikulum_id': self.id_neosia
        })

    def get_ilo_bulk_delete_url(self):
        return reverse('kurikulum:ilo:bulk-delete', kwargs={
            'kurikulum_id': self.id_neosia
        })
