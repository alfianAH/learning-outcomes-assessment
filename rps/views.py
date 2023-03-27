from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from learning_outcomes_assessment.forms.edit import MultiFormView
from ilo.models import Ilo
from mata_kuliah_semester.models import MataKuliahSemester
from rps.models import RencanaPembelajaranSemester
from .forms import (
    RencanaPembelajaranSemesterForm,
    PengembangRPSForm,
    KoordinatorRPSForm,
    DosenPengampuRPSForm,
    MataKuliahSyaratRPSForm,
)


# Create your views here.
class RPSHomeView(TemplateView):
    template_name = 'rps/home.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
    
    @property
    def get_ilo(self):
        ilo_qs = Ilo.objects.filter(
            pi_area__performanceindicator__piclo__clo__mk_semester=self.mk_semester_obj
        ).distinct()

        return ilo_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_rincian_tab = True
        is_pertemuan_tab = False
        
        rps: RencanaPembelajaranSemester = None
        if hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            rps = self.mk_semester_obj.rencanapembelajaransemester

        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'is_rincian_tab': is_rincian_tab,
            'is_pertemuan_tab': is_pertemuan_tab,
            'ilo_object_list': self.get_ilo,
            'rps': rps,
        })
        return context


class RPSCreateView(MultiFormView):
    form_classes = {
        'rps_form': RencanaPembelajaranSemesterForm,
        'pengembang_rps_form': PengembangRPSForm,
        'koordinator_rps_form': KoordinatorRPSForm,
        'dosen_pengampu_rps_form': DosenPengampuRPSForm,
        'mata_kuliah_syarat_rps_form': MataKuliahSyaratRPSForm,
    }
    template_name = 'rps/create-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context
