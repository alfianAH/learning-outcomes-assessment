from django.conf import settings
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
from .forms import(
    SemesterProdiCreateForm,
    SemesterProdiBulkUpdateForm,
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


class SemesterCreateView(FormView):
    form_class = SemesterProdiCreateForm
    template_name = 'semester/create-view.html'
    success_url = reverse_lazy('semester:read-all')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_placeholder': 'Cari nama semester...',
            'back_url': self.success_url,
            'submit_text': 'Tambahkan',
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        print(form.cleaned_data)
        # Get detail semester prodi from Neosia

        # Get or create tahun ajaran

        # Get prodi object

        # Get or create tahun ajaran prodi

        # Get or create semester

        # Create semester prodi

        return super().form_valid(form)


class SemesterBulkUpdateView(FormView):
    form_class = SemesterProdiBulkUpdateForm
    template_name = 'semester/bulk-update-view.html'
    success_url = reverse_lazy('semester:read-all')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        if len(form.fields.get('update_data_semester').choices) == 0:
            messages.info(request, 'Data semester sudah sinkron dengan data di Neosia')
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_placeholder': 'Cari nama semester...',
            'back_url': self.success_url,
            'submit_text': 'Update',
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def update_semester_prodi(self, semester_prodi_id: int):
        try:
            semester_prodi_obj = SemesterProdi.objects.filter(id_neosia=semester_prodi_id)
        except SemesterProdi.DoesNotExist:
            messages.error(self.request, 
                'Semester Prodi dengan ID: {} tidak ditemukan, sehingga gagal mengupdate semester'.format(semester_prodi_id))
            return
        
        # new_semester_data = get_detail_semester_prodi(semester_prodi_id)
        # semester_prodi_obj.update(**new_semester_data)

    def form_valid(self, form) -> HttpResponse:
        print(form.cleaned_data)
        # Get semester prodi ids
        update_semester_data = form.cleaned_data.get('update_data_semester', [])

        # Update semester
        for semester_prodi_id in update_semester_data:
            try:
                semester_prodi_id = int(semester_prodi_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert Semester Prodi ID ("{}") to integer'.format(semester_prodi_id))
                messages.error(self.request, 'Tidak dapat mengonversi Semester Prodi ID: {} ke integer'.format(semester_prodi_id))
                return redirect(self.success_url)

            self.update_semester_prodi(semester_prodi_id)
        
        messages.success(self.request, 'Proses mengupdate semester telah selesai.')

        return super().form_valid(form)


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
