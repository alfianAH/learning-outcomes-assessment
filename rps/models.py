from django.db import models
from mata_kuliah_semester.models import MataKuliahSemester
from lock_model.models import LockableMixin
from learning_outcomes_assessment.validators import validate_pdf_file
from .utils import rps_upload_handler


# Create your models here.
class RencanaPembelajaranSemester(LockableMixin, models.Model):
    mk_semester = models.OneToOneField(MataKuliahSemester, on_delete=models.CASCADE)
    file_rps = models.FileField(null=False, blank=False, upload_to=rps_upload_handler, validators=[validate_pdf_file])
    created_at = models.DateTimeField(auto_now_add=True)
