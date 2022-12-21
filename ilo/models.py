from django.db import models
from django.urls import reverse
from pi_area.models import PerformanceIndicatorArea

# Create your models here.
class Ilo(models.Model):
    pi_area = models.OneToOneField(PerformanceIndicatorArea, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255, null=False)
    deskripsi = models.TextField(null=False)
    satisfactory_level = models.FloatField(null=False)
    persentase_capaian_ilo = models.FloatField(null=True)

    def get_semester(self):
        return self.pi_area.assessment_area.semester

    def read_detail_url(self):
        return reverse('semester:ilo:read', kwargs={
            'semester_kurikulum_id': self.get_semester().pk,
            'ilo_id': self.pk
        })

    def get_hx_ilo_update_url(self):
        return reverse('semester:ilo:hx-update', kwargs={
            'semester_kurikulum_id': self.get_semester().pk,
            'ilo_id': self.pk
        })

    def get_ilo_update_url(self):
        return reverse('semester:ilo:update', kwargs={
            'semester_kurikulum_id': self.get_semester().pk,
            'ilo_id': self.pk
        })
