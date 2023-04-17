from django.db.models.signals import (
    pre_save, 
    pre_delete,
    post_save,
    post_delete,
)
from django.dispatch import receiver
from clo.models import (
    Clo, KomponenClo, PiClo,
)
from pi_area.models import(
    AssessmentArea,
    PerformanceIndicatorArea,
    PerformanceIndicator
)
from lock_model.models import Lock
from rps.models import RencanaPembelajaranSemester


@receiver(pre_save, sender=Clo)
@receiver(pre_save, sender=KomponenClo)
@receiver(pre_save, sender=PiClo)
@receiver(pre_save, sender=AssessmentArea)
@receiver(pre_save, sender=PerformanceIndicatorArea)
@receiver(pre_save, sender=PerformanceIndicator)
@receiver(pre_save, sender=RencanaPembelajaranSemester)
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
@receiver(pre_delete, sender=AssessmentArea)
@receiver(pre_delete, sender=PerformanceIndicatorArea)
@receiver(pre_delete, sender=PerformanceIndicator)
@receiver(pre_delete, sender=RencanaPembelajaranSemester)
def prevent_delete_when_locked(sender, instance, **kwargs):
    if instance.lock and instance.lock.is_locked:
        raise Exception('Model {} (pk={}) is locked and cannot be deleted.'.format(sender.__name__, instance.pk))
    

@receiver(post_delete, sender=Clo)
@receiver(post_delete, sender=KomponenClo)
@receiver(post_delete, sender=PiClo)
@receiver(post_delete, sender=AssessmentArea)
@receiver(post_delete, sender=PerformanceIndicatorArea)
@receiver(post_delete, sender=PerformanceIndicator)
@receiver(post_delete, sender=RencanaPembelajaranSemester)
def delete_lock_object_when_deleted(sender, instance, **kwargs):
    if instance.lock and not instance.lock.is_locked:
        instance.lock.delete()
