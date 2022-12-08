from django.db import models
from ilo.models import Ilo


# Create your models here.
class PerformanceIndicator(models.Model):
    ilo = models.ForeignKey(Ilo, on_delete=models.CASCADE)
    deskripsi = models.TextField()
