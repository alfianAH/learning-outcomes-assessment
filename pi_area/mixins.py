from lock_model.mixins import LockedObjectPermissionMixin
from kurikulum.models import Kurikulum
from .models import AssessmentArea


class PILockedObjectPermissionMixin(LockedObjectPermissionMixin):
    kurikulum_obj: Kurikulum = None
    access_denied_message = 'Performance Indicator sudah dikunci. Jika ingin mengubah atau mengedit, silakan membuka kunci terlebih dahulu.'
    
    def get_locked_object_parent_model(self):
        return self.kurikulum_obj

    def get_locked_object_model(self):
        return AssessmentArea
