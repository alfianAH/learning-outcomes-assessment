from django.db import models
from django.urls import reverse
from kurikulum.models import Kurikulum

# Create your models here.
class ColorChoices(models.TextChoices):
    DEFAULT = 'Default', 'badge-custom-gray'
    RED = 'Merah', 'badge-custom-red'
    ORANGE = 'Orange', 'badge-custom-orange'
    YELLOW = 'Kuning', 'badge-custom-yellow'
    GREEN = 'Hijau', 'badge-custom-green'
    BLUE = 'Biru', 'badge-custom-blue'
    PURPLE = 'Ungu', 'badge-custom-purple'


class AssessmentArea(models.Model):
    kurikulum = models.ForeignKey(Kurikulum, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100, null=False, blank=False)
    color = models.CharField(max_length=7, choices=ColorChoices.choices, null=False, blank=False, default=ColorChoices.DEFAULT)

    class Meta:
        ordering = ['nama']

    def __str__(self) -> str:
        return self.nama

    def get_pi_area(self):
        return self.performanceindicatorarea_set.all()

    def get_hx_update_pi_area_url(self):
        return reverse('kurikulum:pi_area:hx-update', kwargs={
            'kurikulum_id': self.kurikulum.id_neosia,
            'assessment_area_id': self.pk
        })

    def get_update_pi_area_url(self):
        return reverse('kurikulum:pi_area:update', kwargs={
            'kurikulum_id': self.kurikulum.id_neosia,
            'assessment_area_id': self.pk
        })
    
    def get_read_all_pi_area_url(self):
        return reverse('kurikulum:pi_area:read-all', kwargs={
            'kurikulum_id': self.kurikulum.id_neosia
        })

    def get_delete_assessment_area_url(self):
        return reverse('kurikulum:pi_area:assessment-area-delete', kwargs={
            'kurikulum_id': self.kurikulum.id_neosia,
            'assessment_area_id': self.pk
        })


class PerformanceIndicatorArea(models.Model):
    assessment_area = models.ForeignKey(AssessmentArea, on_delete=models.CASCADE)
    pi_code = models.CharField(max_length=20, null=False, blank=False)

    class Meta:
        ordering = ['pi_code']

    def __str__(self) -> str:
        return self.pi_code
    
    def get_performance_indicator(self):
        return self.performanceindicator_set.all()

    def read_detail_url(self):
        return reverse('kurikulum:pi_area:pi-area-read', kwargs={
            'kurikulum_id': self.assessment_area.kurikulum.id_neosia,
            'pi_area_id': self.pk
        })
    
    def get_pi_area_update_url(self):
        return reverse('kurikulum:pi_area:pi-area-update', kwargs={
            'kurikulum_id': self.assessment_area.kurikulum.id_neosia,
            'pi_area_id': self.pk
        })


class PerformanceIndicator(models.Model):
    pi_area = models.ForeignKey(PerformanceIndicatorArea, on_delete=models.CASCADE)
    deskripsi = models.TextField()
