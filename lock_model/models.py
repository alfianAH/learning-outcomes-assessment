from django.db import models

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


User = settings.AUTH_USER_MODEL

# Create your models here.
class Lock(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    locked_at = models.DateTimeField(auto_now_add=True)

    is_locked = models.BooleanField(default=False)
    locked_object = GenericForeignKey('content_type', 'object_id')
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def unlock(self):
        self.is_locked = False
        self.save()


class LockableMixin(models.Model):
    lock = models.ForeignKey(Lock, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def lock_object(self, user) -> bool:
        lock_obj, _ = Lock.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            defaults={'locked_object': self, 'locked_by': user},
        )
        if lock_obj is None: return False

        lock_obj.is_locked = True
        self.lock = lock_obj
        self.save()
        return True

    def unlock_object(self) -> bool:
        # Return if lock is deleted
        if not self.lock: return False
        
        self.lock.unlock()
        return True
    
    @property
    def is_locked(self):
        if self.lock and self.lock.is_locked:
            return True
        return False
