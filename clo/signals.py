from django.db.models import QuerySet
from django.db.models.signals import (
    pre_save, 
    pre_delete,
    post_save,
)
from django.dispatch import receiver
from clo.models import (
    Clo, KomponenClo, PiClo, 
    NilaiKomponenCloPeserta,
)
from mata_kuliah_semester.utils import calculate_nilai_per_clo_mk_semester
from lock_model.models import Lock


@receiver(pre_save, sender=Clo)
@receiver(pre_save, sender=KomponenClo)
@receiver(pre_save, sender=PiClo)
def prevent_save_when_locked(sender, instance, **kwargs):
    if instance.lock and instance.lock.is_locked:
        raise Exception('Model {} (pk={}) is locked and cannot be modified.'.format(sender.__name__, instance.pk))


@receiver(post_save, sender=Lock)
def prevent_lock_save(sender, instance, **kwargs):
    if instance.is_locked:
        instance.locked_object.lock = instance
        pre_save.disconnect(prevent_save_when_locked, sender=instance.locked_object.__class__)
        instance.locked_object.save()
        pre_save.connect(prevent_save_when_locked, sender=instance.locked_object.__class__)


@receiver(pre_delete, sender=Clo)
@receiver(pre_delete, sender=KomponenClo)
@receiver(pre_delete, sender=PiClo)
def prevent_delete_when_locked(sender, instance, **kwargs):
    if instance.lock and instance.lock.is_locked:
        raise Exception('Model {} (pk={}) is locked and cannot be deleted.'.format(sender.__name__, instance.pk))


@receiver(post_save, sender=NilaiKomponenCloPeserta)
def update_status_nilai_peserta(sender, instance: NilaiKomponenCloPeserta, **kwargs):
    peserta_obj = instance.peserta
    list_clo_mk_semester: QuerySet[Clo] = instance.komponen_clo.clo.mk_semester.get_all_clo()
    list_komponen_clo_mk_semester = []

    # Get all komponen CLO in MK Semester
    for clo in list_clo_mk_semester:
        for komponen_clo in clo.get_komponen_clo():
            list_komponen_clo_mk_semester.append(komponen_clo)
    
    # Get all nilai komponen CLO peserta
    list_nilai_komponen_clo_peserta: QuerySet[NilaiKomponenCloPeserta] = peserta_obj.get_all_nilai_komponen_clo_peserta()

    # If peserta has all nilai komponen CLO, update status nilai to True
    if len(list_komponen_clo_mk_semester) == len(list_nilai_komponen_clo_peserta):
        peserta_obj.status_nilai = True
        peserta_obj.save()


@receiver(post_save, sender=NilaiKomponenCloPeserta)
def update_mk_semester_average_clo_achievement(sender, instance: NilaiKomponenCloPeserta, **kwargs):
    peserta_obj = instance.peserta

    # If peserta's status nilai is True, then update avg CLO achievement
    if peserta_obj.status_nilai:
        mk_semester = peserta_obj.kelas_mk_semester.mk_semester
        calculate_nilai_per_clo_mk_semester(mk_semester)
