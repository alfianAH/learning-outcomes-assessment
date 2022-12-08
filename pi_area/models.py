from django.db import models
from django.urls import reverse
from semester.models import SemesterKurikulum

# Create your models here.
class AssessmentArea(models.Model):
    semester = models.ForeignKey(SemesterKurikulum, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)

    def get_pi_area(self):
        return self.performanceindicatorarea_set.all()


class PerformanceIndicatorArea(models.Model):
    assessment_area = models.ForeignKey(AssessmentArea, on_delete=models.CASCADE)
    pi_code = models.CharField(max_length=20)
