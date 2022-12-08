from django.db import models
from semester.models import SemesterKurikulum

# Create your models here.
class AssessmentArea(models.Model):
    semester = models.ForeignKey(SemesterKurikulum, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)


class PerformanceIndicatorArea(models.Model):
    assessment_area = models.ForeignKey(AssessmentArea, on_delete=models.CASCADE)
    pi_code = models.CharField(max_length=20)
