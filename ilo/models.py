from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from pi_area.models import PerformanceIndicatorArea

# Create your models here.
class Ilo(models.Model):
    pi_area = models.OneToOneField(PerformanceIndicatorArea, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255, null=False)
    deskripsi = models.TextField(null=False)
    satisfactory_level = models.FloatField(null=False,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    persentase_capaian_ilo = models.FloatField(null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(satisfactory_level__gte=0.0) & Q(satisfactory_level__lte=100.0),
                name='satisfactory_level_range'
            ),
            CheckConstraint(
                check=Q(persentase_capaian_ilo__gte=0.0) & Q(persentase_capaian_ilo__lte=100.0),
                name='persentase_capaian_ilo_range'
            ),
        )

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
