from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from accounts.enums import RoleChoices
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.list_view.views import DetailWithListViewModelD
from learning_outcomes_assessment.forms.edit import (
    ModelBulkUpdateView,
    ModelBulkDeleteView
)
from semester.models import SemesterProdi
from .forms import (
    MataKuliahSemesterCreateForm,
    KelasMataKuliahSemesterUpdateForm,
)
from mata_kuliah_kurikulum.models import(
    MataKuliahKurikulum
)
from .models import (
    MataKuliahSemester,
    KelasMataKuliahSemester,
    DosenMataKuliah,
    PesertaMataKuliah,
)
from .utils import(
    get_kelas_mk_semester,
    get_dosen_kelas_mk_semester,
    get_kelas_mk_semester_choices,
    get_update_kelas_mk_semester_choices
)


# Create your views here.
class MataKuliahSemesterCreateView(ProgramStudiMixin, FormView):
    form_class = MataKuliahSemesterCreateForm
    template_name: str = 'mata-kuliah-semester/create-view.html'
    semester_obj: SemesterProdi = None
    mk_semester_choices = []

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        semester_prodi_id = kwargs.get('semester_prodi_id')
        self.semester_obj: SemesterProdi = get_object_or_404(SemesterProdi, id_neosia=semester_prodi_id)
        self.program_studi_obj = self.semester_obj.tahun_ajaran_prodi.prodi_jenjang.program_studi

        self.mk_semester_choices = get_kelas_mk_semester_choices(self.semester_obj.id_neosia)

        self.success_url = self.semester_obj.read_detail_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if len(self.mk_semester_choices) == 0:
            messages.info(request, 'Pilihan mata kuliah semester kosong. Ada kemungkinan data sudah disinkronisasi atau mata kuliah pada kurikulum belum ditambahkan.')
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'semester_obj': self.semester_obj,
            'back_url': self.success_url,
            'submit_text': 'Tambahkan'
        })
        return context

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields['mk_from_neosia'].choices = self.mk_semester_choices
        return form

    def form_valid(self, form) -> HttpResponse:
        list_kelas_mk_semester_id = form.cleaned_data.get('mk_from_neosia')
        list_kelas_mk_semester = get_kelas_mk_semester(self.semester_obj.id_neosia)

        for kelas_mk_semester in list_kelas_mk_semester:
            if str(kelas_mk_semester['id']) not in list_kelas_mk_semester_id: continue

            # Get MK Kurikulum object
            mk_kurikulum_id = kelas_mk_semester['id_mata_kuliah']
            try:
                mk_kurikulum_obj = MataKuliahKurikulum.objects.get(id_neosia=mk_kurikulum_id)
            except MataKuliahKurikulum.DoesNotExist:
                if settings.DEBUG:
                    print('MK Kurikulum object not found. ID: {}'.format(mk_kurikulum_id))
                messages.error(self.request, 'Tidak dapat menemukan mata kuliah kurikulum dengan ID: {}'.format(mk_kurikulum_id))
                continue
            except MataKuliahKurikulum.MultipleObjectsReturned:
                if settings.DEBUG:
                    print('MK Kurikulum with ID({}) returns multiple objects.'.format(mk_kurikulum_id))
                continue
            
            # Create MK Semester
            mk_semester_obj, _ = MataKuliahSemester.objects.get_or_create(
                mk_kurikulum=mk_kurikulum_obj,
                semester=self.semester_obj
            )

            # Create Kelas MK Semester
            kelas_mk_semester_obj = KelasMataKuliahSemester.objects.create(
                id_neosia=kelas_mk_semester['id'],
                mk_semester=mk_semester_obj,
                nama=kelas_mk_semester['nama']
            )

            # Get list Dosen Kelas MK Semester
            list_dosen_kelas_mk_semester = get_dosen_kelas_mk_semester(kelas_mk_semester_obj.id_neosia)

            # Create dosen (user) and dosen (Kelas MK Semester) 
            for dosen in list_dosen_kelas_mk_semester:
                user = authenticate(self.request, user=dosen, role=RoleChoices.DOSEN)
                DosenMataKuliah.objects.create(
                    kelas_mk_semester=kelas_mk_semester_obj,
                    dosen=user
                )
        
        messages.success(self.request, 'Proses menambahkan mata kuliah semester sudah selesai. {}'.format(self.request.user.name))

        return super().form_valid(form)


class MataKuliahSemesterReadView(ProgramStudiMixin, DetailWithListViewModelD):
    single_model = MataKuliahSemester
    single_pk_url_kwarg = 'mk_semester_id'
    single_object: MataKuliahSemester = None

    model = PesertaMataKuliah
    template_name = 'mata-kuliah-semester/detail-view.html'

    ordering: str = 'mahasiswa__nama'
    sort_form_ordering_by_key: str = 'ordering_by'

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'peserta-mk-semester-'
    input_name: str = 'id_peserta_mk_semester'
    list_id: str = 'peserta-mk-semester-list-content'
    list_item_name: str = 'mata-kuliah-semester/partials/peserta/list-item-name-peserta-mk-semester.html'
    list_custom_field_template: str = 'mata-kuliah-semester/partials/peserta/list-custom-field-peserta-mk-semester.html'
    list_custom_expand_field_template: str = 'mata-kuliah-semester/partials/peserta/list-custom-expand-field-peserta-mk-semester.html'
    table_custom_expand_field_template: str = 'mata-kuliah-semester/partials/peserta/table-custom-expand-field-peserta-mk-semester.html'
    table_custom_field_header_template: str = 'mata-kuliah-semester/partials/peserta/table-custom-field-header-peserta-mk-semester.html'
    table_custom_field_template: str = 'mata-kuliah-semester/partials/peserta/table-custom-field-peserta-mk-semester.html'
    filter_template: str = 'mata-kuliah-semester/partials/peserta/peserta-mk-semester-filter-form.html'
    sort_template: str = 'mata-kuliah-semester/partials/peserta/peserta-mk-semester-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.program_studi_obj = self.single_object.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
        # self.bulk_delete_url = self.single_object.get_bulk_delete_mk_semester_url()
        # self.reset_url = self.single_object.read_detail_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        peserta_mk_semester_qs = self.get_queryset()

        if peserta_mk_semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            # self.filter_form = MataKuliahSemesterFilter(
            #     data=filter_data or None,
            #     queryset=peserta_mk_semester_qs
            # )
            # self.sort_form = MataKuliahSemesterSort(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            kelas_mk_semester__mk_semester=self.single_object.pk
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'coslpan_length': 8,
        })
        return context


class MataKuliahSemesterBulkDeleteView(ModelBulkDeleteView):
    model = MataKuliahSemester
    id_list_obj = 'id_mk_semester'
    success_msg = 'Berhasil mmenghapus mata kuliah semester'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        semester_prodi_id = kwargs.get('semester_prodi_id')
        semester_prodi_obj = get_object_or_404(SemesterProdi, id_neosia=semester_prodi_id)
        self.success_url = semester_prodi_obj.read_detail_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class KelasMataKuliahSemesterUpdateView(ProgramStudiMixin, ModelBulkUpdateView):
    form_class = KelasMataKuliahSemesterUpdateForm
    template_name: str = 'mata-kuliah-semester/kelas-mk-semester-update-view.html'
    mk_semester_obj: MataKuliahSemester = None

    back_url: str = ''
    form_field_name: str = 'update_data_kelas_mk_semester'
    search_placeholder: str = 'Cari nama mata kuliah...'
    no_choices_msg: str = 'Data mata kuliah semester sudah sinkron dengan data di Neosia'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
        self.success_url = self.mk_semester_obj.read_detail_url()
        self.back_url = self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()        
        kwargs['mk_semester'] = self.mk_semester_obj
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context

    def update_kelas_mk_semester(self, list_kelas_mk_semester_id):
        list_update_kelas_mk_semester = get_update_kelas_mk_semester_choices(self.mk_semester_obj)
        
        for kelas_mk_semester_id, kelas_mk_semester_data in list_update_kelas_mk_semester:
            if str(kelas_mk_semester_id) not in list_kelas_mk_semester_id: continue

            new_kelas_mk_semester = kelas_mk_semester_data['new']
            
            kelas_mk_semester_obj = KelasMataKuliahSemester.objects.filter(id_neosia=kelas_mk_semester_id)
            kelas_mk_semester_obj.update(
                nama=new_kelas_mk_semester['nama']
            )

    def form_valid(self, form) -> HttpResponse:
        update_kelas_mk_semester_data = form.cleaned_data.get(self.form_field_name)

        self.update_kelas_mk_semester(update_kelas_mk_semester_data)
        messages.success(self.request, 'Berhasil mengupdate mata kuliah kurikulum')
        return super().form_valid(form)


class KelasMataKuliahSemesterDeleteView(ProgramStudiMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj: MataKuliahSemester = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.read_detail_url()

        self.program_studi_obj = self.mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        kelas_mk_semester_id = kwargs.get('kelas_mk_semester_id')

        try:
            kelas_mk_semester_obj = KelasMataKuliahSemester.objects.get(id_neosia = kelas_mk_semester_id)
        except KelasMataKuliahSemester.DoesNotExist or KelasMataKuliahSemester.MultipleObjectsReturned:
            messages.error(request, 'Gagal menghapus kelas mata kuliah dengan ID: {}'.format(kelas_mk_semester_id))
            return redirect(self.success_url)
        
        messages.success(request, 'Berhasil menghapus kelas mata kuliah: {}'.format(kelas_mk_semester_obj.nama))
        kelas_mk_semester_obj.delete()
        
        return redirect(self.success_url)
