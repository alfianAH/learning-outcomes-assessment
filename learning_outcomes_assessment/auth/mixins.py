from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from accounts.models import ProgramStudi


class ProgramStudiMixin:
    program_studi_obj: ProgramStudi = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_anonymous :
            return redirect(reverse('accounts:login'))
        
        if self.program_studi_obj.id_neosia == request.user.prodi.id_neosia:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
