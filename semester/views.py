from django.http import Http404, HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from learning_outcomes_assessment.list_view.views import ListViewModelA
from .filters import(
    SemesterProdiFilter,
    SemesterProdiSort
)
from .models import(
    Semester, 
    SemesterProdi,
)


# Create your views here.
class SemesterReadAllView(ListViewModelA):
    model = SemesterProdi
    paginate_by: int = 10
    template_name: str = 'semester/home.html'
    ordering: str = 'semester__nama'
    sort_form_ordering_by_key: str = 'ordering_by'

    semester_filter: SemesterProdiFilter = None
    semester_sort: SemesterProdiSort = None

    bulk_delete_url: str = reverse_lazy('semester:bulk-delete')
    reset_url: str = reverse_lazy('semester:read-all')
    list_id: str = 'semester-list-content'
    input_name: str = 'id_semester'
    list_prefix_id: str = 'semester-'
    list_item_name: str = 'semester/partials/list-item-name-semester-prodi.html'
    badge_template: str = 'semester/partials/badge-list-semester-prodi.html'
    list_custom_field_template: str = 'semester/partials/list-custom-field-semester-prodi.html'
    table_custom_field_header_template: str = 'semester/partials/table-custom-field-header-semester.html'
    table_custom_field_template: str = 'semester/partials/table-custom-field-semester-prodi.html'
    filter_template: str = 'semester/partials/semester-prodi-filter-form.html'
    sort_template: str = 'semester/partials/semester-sort-form.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.prodi is None: raise Http404()

        semester_qs = self.get_queryset()

        if semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'tipe_semester': request.GET.get('tipe_semester', ''),
            }
            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = SemesterProdiFilter(
                data=filter_data or None, 
                queryset=semester_qs
            )
            self.sort_form = SemesterProdiSort(
                data=sort_data, 
                initial={self.sort_form_ordering_by_key: self.ordering}
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        prodi_id = self.request.user.prodi.id_neosia
        
        self.queryset = self.model.objects.filter(
            tahun_ajaran_prodi__prodi__id_neosia=prodi_id
        )
        return super().get_queryset()


class SemesterReadView(DetailView):
    model = SemesterProdi
    pk_url_kwarg: str = 'semester_prodi_id'
    template_name: str = 'semester/detail-view.html'


class SemesterBulkDeleteView(FormView):
    success_url = reverse_lazy('semester:read-all')

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        list_semester_prodi = request.POST.getlist('id_semester')
        list_semester_prodi = [*set(list_semester_prodi)]

        if len(list_semester_prodi) > 0:
            SemesterProdi.objects.filter(id__in=list_semester_prodi).delete()
            messages.success(self.request, 'Berhasil menghapus semester')
        
        return redirect(self.get_success_url())
