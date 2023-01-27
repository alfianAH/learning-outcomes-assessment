from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from learning_outcomes_assessment.list_view.views import ListViewModelA
from mata_kuliah_semester.models import MataKuliahSemester
from .models import Clo


# Create your views here.
class CloReadAllView(ListViewModelA):
    template_name = 'clo/home.html'
    model = Clo
    filter_form = None
    sort_form = None
    sort_form_ordering_by_key: str = 'odering_by'
    ordering = 'nama'

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'list-clo-'
    list_id: str = 'list-content'
    input_name: str = 'id_clo_'
    list_custom_field_template: str = 'clo/partials/list-custom-field-clo.html'
    table_custom_field_header_template: str = 'clo/partials/table-custom-field-header-clo.html'
    table_custom_field_template: str = 'clo/partials/table-custom-field-clo.html'
    filter_template: str = 'clo/partials/clo-filter-form.html'
    sort_template: str = 'clo/partials/clo-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        
        self.reset_url = self.mk_semester_obj.get_clo_read_all_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        clo_qs = self.get_queryset()

        if clo_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', '')
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            mk_semester=self.mk_semester_obj
        )
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context



class CloCreateView(ListViewModelA):
    pass
