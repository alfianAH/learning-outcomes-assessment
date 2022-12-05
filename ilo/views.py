from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView
from django.shortcuts import get_object_or_404
from .models import Ilo
from .forms import IloCreateForm
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
            'semester_obj': self.semester_obj,
            'create_ilo_url': self.semester_obj.create_ilo_url(),
        })
        return context


class IloCreateView(FormView):
    form_class = IloCreateForm
    template_name: str = 'ilo/partials/ilo-create-view.html'
    success_url = reverse_lazy('semester:ilo:read-all')
