from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
from learning_outcomes_assessment.list_view.views import ListViewModelA
from .filters import(
    SemesterFilter,
    SemesterKurikulumFilter,
    SemesterSort,
    SemesterKurikulumSort
)
from .models import(
    Semester, 
    SemesterKurikulum
)


# Create your views here.
class SemesterReadAllView(ListViewModelA):
    model = SemesterKurikulum
    paginate_by: int = 10
    template_name: str = 'semester/home.html'
    ordering: str = 'semester__nama'
    sort_form_ordering_by_key: str = 'ordering_by'

    semester_filter: SemesterKurikulumFilter = None
    semester_sort: SemesterKurikulumSort = None

    bulk_delete_url: str = ''
    reset_url: str = reverse_lazy('semester:read-all')
    list_id: str = 'semester-list-content'
    input_name: str = 'id_semester'
    list_prefix_id: str = 'semester-'
    list_item_name: str = 'semester/partials/list-item-name-semester-kurikulum.html'
    badge_template: str = 'semester/partials/badge-list-semester-kurikulum.html'
    list_custom_field_template: str = 'semester/partials/list-custom-field-semester.html'
    table_custom_field_header_template: str = 'semester/partials/table-custom-field-header-semester.html'
    table_custom_field_template: str = 'semester/partials/table-custom-field-semester-kurikulum.html'
    filter_template: str = 'semester/partials/semester-kurikulum-filter-form.html'
    sort_template: str = 'semester/partials/semester-sort-form.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.prodi is None: raise Http404()

        semester_qs = self.model.objects.filter(kurikulum__prodi__id_neosia=request.user.prodi.id_neosia)

        if semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'tipe_semester': request.GET.get('tipe_semester', ''),
            }
            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = SemesterKurikulumFilter(
                data=filter_data or None, 
                queryset=semester_qs
            )
            self.sort_form = SemesterKurikulumSort(
                data=sort_data, 
                initial={self.sort_form_ordering_by_key: self.ordering}
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        prodi_id = self.request.user.prodi.id_neosia
        
        self.queryset = self.model.objects.filter(
            kurikulum__prodi__id_neosia=prodi_id
        )
        return super().get_queryset()


class SemesterReadView(DetailView):
    model = SemesterKurikulum
    pk_url_kwarg: str = 'semester_kurikulum_id'
    template_name: str = 'semester/detail-view.html'
