from django.db import models
from learning_outcomes_assessment.utils import get_reverse_url
from accounts.models import ProgramStudiJenjang


# Create your models here.
class Kurikulum(models.Model):
    id_neosia = models.BigIntegerField(unique=True, null=False, primary_key=True)
    prodi_jenjang = models.ForeignKey(ProgramStudiJenjang, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255, null=False)
    tahun_mulai = models.IntegerField(null=False)
    is_active = models.BooleanField(null=False)

    is_assessmentarea_locked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.nama
    
    @property
    def get_kwargs(self):
        return {
            'kurikulum_id': self.pk
        }

    def read_sync_url(self):
        return get_reverse_url('kurikulum:read-sync', self.get_kwargs)

    def read_detail_url(self):
        return get_reverse_url('kurikulum:read', self.get_kwargs)

    # Mata Kuliah Kurikulum
    def get_mk_kurikulum(self):
        return self.matakuliahkurikulum_set.all()
    
    def read_all_mk_kurikulum_url(self):
        return get_reverse_url('kurikulum:mata_kuliah_kurikulum:read-all', self.get_kwargs)

    def get_bulk_delete_mk_kurikulum_url(self):
        return get_reverse_url('kurikulum:mata_kuliah_kurikulum:bulk-delete', self.get_kwargs)
    
    def get_create_mk_kurikulum_url(self):
        return get_reverse_url('kurikulum:mata_kuliah_kurikulum:create', self.get_kwargs)

    def get_bulk_update_mk_kurikulum_url(self):
        return get_reverse_url('kurikulum:mata_kuliah_kurikulum:bulk-update', self.get_kwargs)

    # Performance Indicator Area
    def read_all_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:read-all', self.get_kwargs)

    def get_hx_create_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:hx-create', self.get_kwargs)

    def get_create_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:create', self.get_kwargs)

    def get_bulk_delete_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:pi-area-bulk-delete', self.get_kwargs)

    def get_duplicate_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:duplicate', self.get_kwargs)

    # ILO
    def read_all_ilo_url(self):
        return get_reverse_url('kurikulum:ilo:read-all', self.get_kwargs)

    def get_hx_create_ilo_url(self):
        return get_reverse_url('kurikulum:ilo:hx-create', self.get_kwargs)

    def get_create_ilo_url(self):
        return get_reverse_url('kurikulum:ilo:create', self.get_kwargs)

    def get_ilo_bulk_delete_url(self):
        return get_reverse_url('kurikulum:ilo:bulk-delete', self.get_kwargs)
