from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from learning_outcomes_assessment.forms.edit import MultiFormView
from mata_kuliah_semester.models import MataKuliahSemester


# Create your views here.
class RPSHomeView(TemplateView):
    template_name = 'rps/home.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_rincian_tab = True
        is_pertemuan_tab = False

        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'is_rincian_tab': is_rincian_tab,
            'is_pertemuan_tab': is_pertemuan_tab,
        })
        return context


class RPSCreateView(MultiFormView):
    pass
