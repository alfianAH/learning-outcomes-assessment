from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from accounts.models import ProgramStudi
from mata_kuliah_semester.models import PesertaMataKuliah


class ProgramStudiMixin:
    program_studi_obj: ProgramStudi = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_anonymous :
            return redirect(reverse('accounts:login'))
        
        if self.program_studi_obj.id_neosia == request.user.prodi.id_neosia:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class MahasiswaMixin:
    peserta_mk: PesertaMataKuliah = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        if user.is_anonymous :
            return redirect(reverse('accounts:login'))
        
        # If user's role is admin or dosen, skip
        if user.role != 'm':
            return super().dispatch(request, *args, **kwargs)
        
        if self.peserta_mk.mahasiswa == user:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
