from django.db.models.signals import (
    post_delete,
)
from django.dispatch import receiver
from mata_kuliah_semester.models import PesertaMataKuliah
from mata_kuliah_semester.utils import calculate_nilai_per_clo_mk_semester


@receiver(post_delete, sender=PesertaMataKuliah)
def update_mk_semester_average_clo_achievement(sender, instance: PesertaMataKuliah, **kwargs):
    mk_semester = instance.kelas_mk_semester.mk_semester
    calculate_nilai_per_clo_mk_semester(mk_semester)
