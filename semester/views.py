from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from learning_outcomes_assessment.forms.edit import (
    ModelBulkDeleteView,
    ModelBulkUpdateView
)
from learning_outcomes_assessment.list_view.views import (
    ListViewModelA,
    DetailWithListViewModelA,
)
from mata_kuliah_semester.filters import MataKuliahSemesterFilter, MataKuliahSemesterSort
from mata_kuliah_semester.models import MataKuliahSemester
from .filters import(
    SemesterProdiFilter,
    SemesterProdiSort
)
from .forms import(
    SemesterProdiCreateForm,
    SemesterProdiBulkUpdateForm,
)
from accounts.models import ProgramStudi
from .models import(
    TahunAjaran,
    TahunAjaranProdi,
    TipeSemester,
    Semester, 
    SemesterProdi,
)
from .utils import(
    get_semester_prodi
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
        if request.user.prodi is None: raise PermissionDenied()

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
        # Get prodi object
        prodi_obj: ProgramStudi = self.request.user.prodi

        list_semester_prodi_id = form.cleaned_data.get('semester_from_neosia')
        list_semester_prodi = get_semester_prodi(prodi_obj.id_neosia)
        
        # Get detail semester prodi from Neosia
        for semester_prodi in list_semester_prodi:
            if str(semester_prodi['id_neosia']) not in list_semester_prodi_id: continue

            # Get or create tahun ajaran
            tahun_ajaran_obj, _ = TahunAjaran.objects.get_or_create_tahun_ajaran(semester_prodi['tahun_ajaran'])

            # Get or create tahun ajaran prodi
            tahun_ajaran_prodi_obj, _ = TahunAjaranProdi.objects.get_or_create(
                tahun_ajaran=tahun_ajaran_obj,
                prodi=prodi_obj
            )

            # Get tipe semester
            match(semester_prodi['tipe_semester']): 
                case 'ganjil':
                    tipe_semester = TipeSemester.GANJIL
                case 'genap':
                    tipe_semester = TipeSemester.GENAP

            # Get or create semester
            semester_obj, _ = Semester.objects.get_or_create(
                id_neosia=semester_prodi['id_semester'],
                tahun_ajaran=tahun_ajaran_obj,
                nama=semester_prodi['nama'],
                tipe_semester=tipe_semester
            )

            # Create semester prodi
            SemesterProdi.objects.create(
                id_neosia=semester_prodi['id_neosia'],
                tahun_ajaran_prodi=tahun_ajaran_prodi_obj,
                semester=semester_obj
            )

        messages.success(self.request, 'Berhasil menambahkan semester')

        return super().form_valid(form)


class SemesterBulkUpdateView(ModelBulkUpdateView):
    form_class = SemesterProdiBulkUpdateForm
    template_name = 'semester/bulk-update-view.html'
    success_url = reverse_lazy('semester:read-all')

    back_url: str = reverse_lazy('semester:read-all')
    form_field_name: str = 'update_data_semester'
    search_placeholder: str = 'Cari nama semester...'
    no_choices_msg: str = 'Data semester sudah sinkron dengan data di Neosia'

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
        # TODO: not yet implemented
        # new_semester_data = get_detail_semester_prodi(semester_prodi_id)
        # semester_prodi_obj.update(**new_semester_data)

    def form_valid(self, form) -> HttpResponse:
        # Get semester prodi ids
        update_semester_data = form.cleaned_data.get(self.form_field_name, [])

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


class SemesterReadView(DetailWithListViewModelA):
    single_model = SemesterProdi
    single_pk_url_kwarg = 'semester_prodi_id'
    single_object: SemesterProdi = None
    
    model = MataKuliahSemester
    paginate_by: int = 10
    template_name: str = 'semester/detail-view.html'
    ordering: str = 'mk_kurikulum__nama'
    sort_form_ordering_by_key: str = 'ordering_by'

    filter_form: MataKuliahSemesterFilter = None
    sort_form: MataKuliahSemesterSort = None

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'mk-semester-'
    input_name: str = 'id_mk_semester'
    list_id: str = 'mk-semester-list-content'
    list_item_name: str = 'mata-kuliah-semester/partials/list-item-name-mk-semester.html'
    list_custom_field_template: str = 'mata-kuliah-semester/partials/list-custom-field-mk-semester.html'
    table_custom_field_header_template: str = 'mata-kuliah-semester/partials/table-custom-field-header-mk-semester.html'
    table_custom_field_template: str = 'mata-kuliah-semester/partials/table-custom-field-mk-semester.html'
    filter_template: str = 'mata-kuliah-semester/partials/mk-semester-filter-form.html'
    sort_template: str = 'mata-kuliah-semester/partials/mk-semester-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.bulk_delete_url = self.single_object.get_bulk_delete_mk_semester_url()
        self.reset_url = self.single_object.read_detail_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        mk_semester_qs = self.get_queryset()

        if mk_semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'sks': request.GET.get('sks', ''),
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = MataKuliahSemesterFilter(
                data=filter_data or None,
                queryset=mk_semester_qs
            )
            self.sort_form = MataKuliahSemesterSort(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            semester=self.single_object.pk
        )
        return super().get_queryset()


class SemesterBulkDeleteView(ModelBulkDeleteView):
    success_url = reverse_lazy('semester:read-all')
    model = SemesterProdi
    id_list_obj: str = 'id_semester'
    success_msg = 'Berhasil menghapus semester'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id_neosia__in=self.get_list_selected_obj())
        return super().get_queryset()
