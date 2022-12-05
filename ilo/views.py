from django.http import HttpRequest, HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from .models import Ilo
from semester.models import SemesterKurikulum


# Create your views here.
class IloReadAllView(ListView):
    model = Ilo
    paginate_by: int = 10
    template_name: str = 'ilo/home.html'
    ordering = ['nama']
    semester_obj: SemesterKurikulum = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        semester_id = kwargs.pop('semester_kurikulum_id')
        self.semester_obj = get_object_or_404(SemesterKurikulum, id=semester_id)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'semester_obj': self.semester_obj
        })
        return context
