from django.db import models
from django.urls import reverse
from pi_area.models import PerformanceIndicatorArea

# Create your models here.
class Ilo(models.Model):
    pi_area = models.ForeignKey(PerformanceIndicatorArea, on_delete=models.CASCADE)

    nama = models.CharField(max_length=255, null=False)
    deskripsi = models.TextField(null=False)
    satisfactory_level = models.FloatField(null=False)
    persentase_capaian_ilo = models.FloatField(null=True)

    def read_semester(self):
        return reverse('semester:read', kwargs={
            'semester_id': self.semester.pk
        })
