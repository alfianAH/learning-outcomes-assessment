from django.db import models
from django.urls import reverse
from semester.models import SemesterKurikulum

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
    semester = models.ForeignKey(SemesterKurikulum, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100, null=False, blank=False)
    color = models.CharField(max_length=7, choices=ColorChoices.choices, null=False, blank=False, default=ColorChoices.DEFAULT)

    def __str__(self) -> str:
        return self.nama

    def get_pi_area(self):
        return self.performanceindicatorarea_set.all()

    def get_update_assessment_area_url(self):
        return reverse('semester:pi_area:hx-assessment-area-update', kwargs={
            'semester_kurikulum_id': self.semester.pk,
            'assessment_area_id': self.pk
        })
    
    def get_read_all_pi_area_url(self):
        return reverse('semester:pi_area:read-all', kwargs={
            'semester_kurikulum_id': self.semester.pk
        })

    def get_delete_assessment_area_url(self):
        return reverse('semester:pi_area:assessment-area-delete', kwargs={
            'semester_kurikulum_id': self.semester.pk,
            'assessment_area_id': self.pk
        })

    def get_hx_create_pi_area_url(self):
        return reverse('semester:pi_area:hx-pi-area-create', kwargs={
            'semester_kurikulum_id': self.semester.pk,
            'assessment_area_id': self.pk
        })


class PerformanceIndicatorArea(models.Model):
    assessment_area = models.ForeignKey(AssessmentArea, on_delete=models.CASCADE)
    pi_code = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self) -> str:
        return self.pi_code

    def read_detail_url(self):
        return reverse('semester:pi_area:pi-area-read', kwargs={
            'semester_kurikulum_id': self.assessment_area.semester.pk,
            'pi_area_id': self.pk
        })
