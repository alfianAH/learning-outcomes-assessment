from lock_model.mixins import LockedObjectPermissionMixin
from mata_kuliah_semester.models import MataKuliahSemester
from .models import RencanaPembelajaranSemester


class RPSLockedObjectPermissionMixin(LockedObjectPermissionMixin):
    """To prevent access if RPS is locked
    Required fields:
        self.mk_semester_obj
    """
    mk_semester_obj: MataKuliahSemester = None
    access_denied_message = 'RPS sudah dikunci. Jika ingin mengubah atau mengedit, silakan membuka kunci terlebih dahulu.'
    
    def get_locked_object_parent_model(self):
        return self.mk_semester_obj

    def get_locked_object_model(self):
        return RencanaPembelajaranSemester