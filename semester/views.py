from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
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
class SemesterReadAllView(ListView):
    model = SemesterKurikulum
    paginate_by: int = 10
    template_name: str = 'semester/home.html'
    ordering: str = 'semester__nama'
    semester_filter: SemesterKurikulumFilter = None
    semester_sort: SemesterKurikulumSort = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.prodi is None: raise Http404()

        semester_qs = self.model.objects.filter(kurikulum__prodi__id_neosia=request.user.prodi.id_neosia)

        if semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'tipe_semester': request.GET.get('tipe_semester', ''),
            }
            sort_data = {
                'ordering_by': request.GET.get('ordering_by', self.ordering)
            }

            self.semester_filter = SemesterKurikulumFilter(
                data=filter_data or None, 
                queryset=semester_qs
            )
            self.semester_sort = SemesterKurikulumSort(data=sort_data, initial={'ordering_by': 'semester__nama'})

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.semester_filter is not None:
            self.queryset = self.semester_filter.qs
        else:
            prodi_id = self.request.user.prodi.id_neosia

            self.queryset = self.model.objects.filter(
                kurikulum__prodi__id_neosia=prodi_id
            )
        return super().get_queryset()

    def get_ordering(self):
        if self.semester_sort is None:
            return super().get_ordering()
        
        if self.semester_sort.is_valid():
            self.ordering = self.semester_sort.cleaned_data.get('ordering_by', 'semester__nama')
        
        return super().get_ordering()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            # 'bulk_delete_url': reverse('semester:bulk-delete'),
            'reset_url': reverse('semester:read-all'),
            'semester_list_prefix_id': 'semester-',
            'badge_template': 'semester/partials/badge-list-semester-kurikulum.html',
            'list_item_name': 'semester/partials/list-item-name-semester-kurikulum.html',
            'list_custom_field_template': 'semester/partials/list-custom-field-semester.html',
            'table_custom_field_header_template': 'semester/partials/table-custom-field-header-semester.html',
            'table_custom_field_template': 'semester/partials/table-custom-field-semester-kurikulum.html',
            'filter_template': 'semester/partials/semester-kurikulum-filter-form.html',
            'sort_template': 'semester/partials/semester-sort-form.html',
        })

        if self.semester_filter is not None:
            context['filter_form'] = self.semester_filter.form
            context['data_exist'] = True

        if self.semester_sort is not None:
            context['sort_form'] = self.semester_sort
        return context


class SemesterReadView(DetailView):
    model = SemesterKurikulum
    pk_url_kwarg: str = 'semester_kurikulum_id'
