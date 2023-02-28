from django.db import models
from learning_outcomes_assessment.utils import get_reverse_url
from kurikulum.models import Kurikulum
from lock_model.models import LockableMixin


# Create your models here.
class ColorChoices(models.TextChoices):
    DEFAULT = 'Default', 'badge-custom-gray'
    RED = 'Merah', 'badge-custom-red'
    ORANGE = 'Orange', 'badge-custom-orange'
    YELLOW = 'Kuning', 'badge-custom-yellow'
    GREEN = 'Hijau', 'badge-custom-green'
    BLUE = 'Biru', 'badge-custom-blue'
    PURPLE = 'Ungu', 'badge-custom-purple'


class AssessmentArea(LockableMixin, models.Model):
    kurikulum = models.ForeignKey(Kurikulum, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100, null=False, blank=False)
    color = models.CharField(max_length=7, choices=ColorChoices.choices, null=False, blank=False, default=ColorChoices.DEFAULT)

    class Meta:
        ordering = ['nama']

    def __str__(self) -> str:
        return self.nama
    
    @property
    def get_kwargs(self):
        return {
            **self.kurikulum.get_kwargs,
            'assessment_area_id': self.pk
        }

    def get_pi_area(self):
        return self.performanceindicatorarea_set.all()

    def get_hx_update_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:hx-update', self.get_kwargs)

    def get_update_pi_area_url(self):
        return get_reverse_url('kurikulum:pi_area:update', self.get_kwargs)

    def get_delete_assessment_area_url(self):
        return get_reverse_url('kurikulum:pi_area:assessment-area-delete', self.get_kwargs)


class PerformanceIndicatorArea(LockableMixin, models.Model):
    assessment_area = models.ForeignKey(AssessmentArea, on_delete=models.CASCADE)
    pi_code = models.CharField(max_length=20, null=False, blank=False)

    class Meta:
        ordering = ['pi_code']

    def __str__(self) -> str:
        return self.pi_code
    
    @property
    def get_kwargs(self):
        return {
            **self.assessment_area.kurikulum.get_kwargs,
            'pi_area_id': self.pk
        }
    
    def get_performance_indicator(self):
        return self.performanceindicator_set.all()

    def read_detail_url(self):
        return get_reverse_url('kurikulum:pi_area:pi-area-read',  self.get_kwargs)
    
    def get_pi_area_update_url(self):
        return get_reverse_url('kurikulum:pi_area:pi-area-update',  self.get_kwargs)


class PerformanceIndicator(LockableMixin, models.Model):
    pi_area = models.ForeignKey(PerformanceIndicatorArea, on_delete=models.CASCADE)
    deskripsi = models.TextField()
