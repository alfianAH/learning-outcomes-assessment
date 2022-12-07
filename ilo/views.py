from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView, CreateView
from django.shortcuts import get_object_or_404
from learning_outcomes_assessment.list_view.views import ListViewModelA
from .models import Ilo
from .filters import (
    IloFilter,
    IloSort,
)
from .forms import IloCreateForm
from semester.models import SemesterKurikulum


# Create your views here.
class IloReadAllView(ListViewModelA):
    model = Ilo
    paginate_by: int = 10
    template_name: str = 'ilo/home.html'
    ordering: str = 'nama'
    sort_form_ordering_by_key: str = 'ordering_by'
    semester_obj: SemesterKurikulum = None

    filter_form: IloFilter = None
    sort_form: IloSort = None
    
    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'ilo-'
    input_name: str = 'id_ilo'
    list_id: str = 'ilo-list-content'
    list_custom_field_template: str = 'ilo/partials/list-custom-field-ilo.html'
    table_custom_field_header_template: str = 'ilo/partials/table-custom-field-header-ilo.html'
    table_custom_field_template: str = 'ilo/partials/table-custom-field-ilo.html'
    filter_template: str = 'ilo/partials/ilo-filter-form.html'
    sort_template: str = 'ilo/partials/ilo-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.reset_url = self.semester_obj.read_all_ilo_url()
        return super().setup(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ilo_qs = self.model.objects.filter(semester=self.semester_obj.pk)

        if ilo_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'satisfactory_level_min': request.GET.get('satisfactory_level_min', ''),
                'satisfactory_level_max': request.GET.get('satisfactory_level_max', ''),
                'persentase_capaian_ilo_min': request.GET.get('persentase_capaian_ilo_min', ''),
                'persentase_capaian_ilo_max': request.GET.get('persentase_capaian_ilo_max', ''),
            }
            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = IloFilter(
                data=filter_data or None, 
                queryset=ilo_qs
            )
            self.sort_form = IloSort(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(semester=self.semester_obj.pk)
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'semester_obj': self.semester_obj,
            'create_ilo_url': self.semester_obj.create_ilo_url(),
        })
        return context


class IloCreateHxView(CreateView):
    model = Ilo
    form_class = IloCreateForm
    template_name: str = 'ilo/partials/ilo-create-view.html'
    semester_obj: SemesterKurikulum = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.success_url = self.semester_obj.read_all_ilo_url()
        return super().setup(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.htmx: raise Http404
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.htmx: raise Http404
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'create_ilo_url': self.semester_obj.create_ilo_url()
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        self.object: Ilo = form.save(commit=False)
        self.object.semester = self.semester_obj
        self.object.save()

        return super().form_valid(form)
