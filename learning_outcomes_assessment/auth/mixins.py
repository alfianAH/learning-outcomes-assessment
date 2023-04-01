from django.db.models import QuerySet
from django.http import HttpRequest, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from accounts.models import ProgramStudi
from mata_kuliah_semester.models import (
    MataKuliahSemester,
    PesertaMataKuliah
)


class ProgramStudiMixin:
    """Program Studi Mixin to prevent other program studi access other program studi file
    Required fields:
        self.program_studi_obj
    """
    program_studi_obj: ProgramStudi = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_anonymous :
            return redirect(reverse('accounts:login'))
        
        if self.program_studi_obj.id_neosia == request.user.prodi.id_neosia:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class MahasiswaAsPesertaMixin:
    """Raise PermissionDenied if mahasiswa access other mahasiswa's URLs
    Required fields:
        self.user
    """

    user = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        if user.is_anonymous :
            return redirect(reverse('accounts:login'))
        
        # If user's role is admin or dosen, skip
        if user.role != 'm':
            return super().dispatch(request, *args, **kwargs)
        
        if self.user != user:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)


class MahasiswaAndMKSemesterMixin:
    """Raise Http404 if mahasiswa access Mata Kuliah Semester that they don't have

    Required field:
        self.mk_semester_obj
    """
    mk_semester_obj: MataKuliahSemester = None
    peserta_mk_semester_qs: QuerySet[PesertaMataKuliah] = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        if user.is_anonymous :
            return redirect(reverse('accounts:login'))
        
        # If user's role is admin or dosen, skip
        if user.role != 'm':
            return super().dispatch(request, *args, **kwargs)
        
        if self.peserta_mk_semester_qs is None:
            self.peserta_mk_semester_qs = PesertaMataKuliah.objects.filter(
                mahasiswa=user,
                kelas_mk_semester__mk_semester=self.mk_semester_obj
            )

        if self.peserta_mk_semester_qs.exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404
