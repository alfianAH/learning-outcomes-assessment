from django.db.models.signals import (
    pre_save, 
    pre_delete,
    post_save,
)
from django.dispatch import receiver
from clo.models import Clo, KomponenClo, PiClo
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

