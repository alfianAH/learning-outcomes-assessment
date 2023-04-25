from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.forms.edit import ModelBulkDeleteView
from learning_outcomes_assessment.forms.views import (
    HtmxCreateFormView,
    HtmxUpdateFormView,
)
from learning_outcomes_assessment.list_view.views import ListViewModelA
from .models import Ilo
from .filters import (
    IloFilter,
    IloSort,
)
from .forms import IloForm
from kurikulum.models import Kurikulum


# Create your views here.
class IloReadAllView(ProgramStudiMixin, PermissionRequiredMixin, ListViewModelA):
    permission_required = ('ilo.view_ilo',)
    model = Ilo
    paginate_by: int = 10
    template_name: str = 'ilo/home.html'
    sort_form_ordering_by_key: str = 'ordering_by'
    kurikulum_obj: Kurikulum = None

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
        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi

        self.bulk_delete_url = self.kurikulum_obj.get_ilo_bulk_delete_url()
        self.reset_url = self.kurikulum_obj.read_all_ilo_url()

        return super().setup(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ilo_qs = self.get_queryset()

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
        self.queryset = self.model.objects.filter(
            pi_area__assessment_area__kurikulum=self.kurikulum_obj.id_neosia)
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'create_ilo_url': self.kurikulum_obj.get_hx_create_ilo_url(),
        })
        return context


class IloReadView(ProgramStudiMixin, PermissionRequiredMixin, DetailView):
    permission_required = ('ilo.view_ilo',)
    model = Ilo
    pk_url_kwarg: str = 'ilo_id'
    template_name: str = 'ilo/ilo-detail-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.object: Ilo = self.get_object()
        kurikulum_obj: Kurikulum = self.object.get_kurikulum()
        self.program_studi_obj = kurikulum_obj.prodi_jenjang.program_studi


class IloCreateView(ProgramStudiMixin, PermissionRequiredMixin, HtmxCreateFormView):
    permission_required = ('ilo.add_ilo',)
    model = Ilo
    form_class = IloForm
    kurikulum_obj: Kurikulum = None

    modal_title: str = 'Tambah CPL'
    modal_content_id: str = 'create-modal-content'
    button_text: str = 'Tambah'
    success_msg: str = 'Berhasil menambahkan CPL'
    error_msg: str = 'Gagal menambahkan CPL. Pastikan data yang anda masukkan valid.'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        self.post_url = self.kurikulum_obj.get_create_ilo_url()
        self.success_url = self.kurikulum_obj.read_all_ilo_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'kurikulum_obj': self.kurikulum_obj
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        self.object: Ilo = form.save(commit=False)
        self.object.save()

        return super().form_valid(form)


class IloUpdateView(ProgramStudiMixin, PermissionRequiredMixin, HtmxUpdateFormView):
    permission_required = ('ilo.change_ilo',)
    model = Ilo
    form_class = IloForm
    pk_url_kwarg = 'ilo_id'
    object: Ilo = None

    modal_title: str = 'Update CPL'
    modal_content_id: str = 'update-modal-content'
    button_text: str = 'Update'
    post_url: str = ''
    success_msg: str = 'Berhasil mengupdate CPL'
    error_msg: str = 'Gagal mengupdate CPL. Pastikan data yang anda masukkan valid.'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        self.object: Ilo = self.get_object()
        self.post_url = self.object.get_ilo_update_url()
        self.success_url = self.object.read_detail_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'kurikulum_obj': self.kurikulum_obj
        })
        return kwargs


class IloBulkDeleteView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkDeleteView):
    permission_required = ('ilo.delete_ilo',)
    model = Ilo
    id_list_obj: str = 'id_ilo'
    success_msg = 'Berhasil menghapus CPL'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        kurikulum_id = kwargs.get('kurikulum_id')
        kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.program_studi_obj = kurikulum_obj.prodi_jenjang.program_studi
        self.success_url = kurikulum_obj.read_all_ilo_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()
