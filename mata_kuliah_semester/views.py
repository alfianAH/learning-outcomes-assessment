from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from accounts.enums import RoleChoices
from clo.models import KomponenClo
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.list_view.views import DetailWithListViewModelD
from learning_outcomes_assessment.forms.edit import (
    ModelBulkUpdateView,
    ModelBulkDeleteView
)
from semester.models import SemesterProdi
from .filters import (
    PesertaMataKuliahFilter,
    PesertaMataKuliahSortForm,
)
from clo.forms import (
    NilaiKomponenCloPesertaFormset,
)
from .forms import (
    MataKuliahSemesterCreateForm,
    KelasMataKuliahSemesterUpdateForm,
    PesertaMataKuliahSemesterCreateForm,
    PesertaMataKuliahSemesterUpdateForm,
)
from mata_kuliah_kurikulum.models import(
    MataKuliahKurikulum
)
from clo.models import(
    NilaiKomponenCloPeserta
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
    get_update_kelas_mk_semester_choices,
    get_peserta_kelas_mk_semester,
    get_peserta_kelas_mk_semester_choices,
    get_update_peserta_mk_semester_choices,
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
                DosenMataKuliah.objects.get_or_create(
                    kelas_mk_semester=kelas_mk_semester_obj,
                    dosen=user
                )
        
        messages.success(self.request, 'Proses menambahkan mata kuliah semester sudah selesai')

        return super().form_valid(form)


class MataKuliahSemesterReadView(ProgramStudiMixin, DetailWithListViewModelD):
    single_model = MataKuliahSemester
    single_pk_url_kwarg = 'mk_semester_id'
    single_object: MataKuliahSemester = None

    model = PesertaMataKuliah
    template_name = 'mata-kuliah-semester/detail-view.html'
    ordering: str = 'mahasiswa__username'
    sort_form_ordering_by_key: str = 'ordering_by'

    filter_form: PesertaMataKuliahFilter = None
    sort_form: PesertaMataKuliahSortForm = None

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'peserta-mk-semester-'
    input_name: str = 'id_peserta_mk_semester'
    list_id: str = 'peserta-mk-semester-list-content'
    list_item_name: str = 'mata-kuliah-semester/partials/peserta/list-item-name-peserta-mk-semester.html'
    list_edit_template: str = 'mata-kuliah-semester/partials/peserta/list-edit-peserta-mk-semester.html'
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
        self.bulk_delete_url = self.single_object.get_peserta_mk_semester_bulk_delete_url()
        self.reset_url = self.single_object.read_detail_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        peserta_mk_semester_qs = self.get_queryset()

        if peserta_mk_semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'nilai_akhir_min': request.GET.get('nilai_akhir_min', ''),
                'nilai_akhir_max': request.GET.get('nilai_akhir_max', ''),
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = PesertaMataKuliahFilter(
                data=filter_data or None,
                queryset=peserta_mk_semester_qs
            )
            self.sort_form = PesertaMataKuliahSortForm(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            kelas_mk_semester__mk_semester=self.single_object.pk
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedoman_objects = [
            {
                'badge_type': 'badge-warning',
                'badge_text': 'Belum dikunci',
                'title': 'Course Learning Outcomes (CLO)',
                'read_detail_url': self.single_object.get_clo_read_all_url()
            },
            {
                'badge_type': 'badge-warning',
                'badge_text': 'Belum dikunci',
                'title': 'Rencana Pembelajaran Semester (RPS)'
            }
        ]
        context.update({
            'colspan_length': 8,
            'pedoman_objects': pedoman_objects
        })

        if self.request.GET.get('nama') or self.request.GET.get('nilai_akhir_min') or self.request.GET.get('nilai_akhir_max') or self.request.GET.get(self.sort_form_ordering_by_key) or self.request.GET.get('active_tab') == 'peserta':
            context['is_peserta_pane'] = True
        else:
            context['is_peserta_pane'] = False
        
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

        self.choices = get_update_kelas_mk_semester_choices(self.mk_semester_obj)

        self.success_url = self.mk_semester_obj.read_detail_url()
        self.back_url = self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context

    def update_kelas_mk_semester(self, list_kelas_mk_semester_id):
        for kelas_mk_semester_id, kelas_mk_semester_data in self.choices:
            if str(kelas_mk_semester_id) not in list_kelas_mk_semester_id: continue

            new_kelas_mk_semester = kelas_mk_semester_data['new']
            
            kelas_mk_semester_obj = KelasMataKuliahSemester.objects.filter(id_neosia=kelas_mk_semester_id)
            kelas_mk_semester_obj.update(
                nama=new_kelas_mk_semester['nama']
            )

    def form_valid(self, form) -> HttpResponse:
        update_kelas_mk_semester_data = form.cleaned_data.get(self.form_field_name)

        self.update_kelas_mk_semester(update_kelas_mk_semester_data)
        messages.success(self.request, 'Berhasil mengupdate mata kuliah semester')
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


# Peserta Mata Kuliah
class PesertaMataKuliahSemesterCreateView(ProgramStudiMixin, FormView):
    form_class = PesertaMataKuliahSemesterCreateForm
    mk_semester_obj: MataKuliahSemester = None
    template_name = 'mata-kuliah-semester/peserta/create-view.html'
    peserta_mk_choices = []

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')

        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        
        self.program_studi_obj = self.mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
        self.peserta_mk_choices = get_peserta_kelas_mk_semester_choices(self.mk_semester_obj)
        self.success_url = '{}?active_tab={}'.format(
            self.mk_semester_obj.read_detail_url(), 
            'peserta'
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if len(self.peserta_mk_choices) == 0:
            messages.info(request, 'Pilihan peserta mata kuliah semester kosong.')
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'back_url': self.success_url,
            'submit_text': 'Tambahkan'
        })
        return context
    
    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields['peserta_mk_from_neosia'].choices = self.peserta_mk_choices
        return form
    
    def form_valid(self, form) -> HttpResponse:
        list_peserta_mk_semester_id = form.cleaned_data.get('peserta_mk_from_neosia')
        list_peserta_mk_semester = get_peserta_kelas_mk_semester(self.mk_semester_obj)

        for peserta_mk in list_peserta_mk_semester:
            if str(peserta_mk['id_neosia']) not in list_peserta_mk_semester_id: continue

            # Get kelas MK Semester
            kelas_mk_semester_id = peserta_mk['id_kelas_mk_semester']
            try: 
                kelas_mk_semester_obj = KelasMataKuliahSemester.objects.get(id_neosia=kelas_mk_semester_id)
            except KelasMataKuliahSemester.DoesNotExist or KelasMataKuliahSemester.MultipleObjectsReturned:
                if settings.DEBUG:
                    print('Kelas MK Semester cannot be found. ID: {}'.format(kelas_mk_semester_id))

                messages.error(self.request, 'Gagal menambahkan peserta mata kuliah. Error: Object Kelas MK Semester tidak dapat ditemukan, ID: {}'.format(kelas_mk_semester_id))
                break
            
            # Create user peserta
            user = authenticate(self.request, user=peserta_mk['mahasiswa'], role=RoleChoices.MAHASISWA)
            # Create peserta MK
            PesertaMataKuliah.objects.create(
                id_neosia=peserta_mk['id_neosia'],
                kelas_mk_semester=kelas_mk_semester_obj,
                mahasiswa=user,
                nilai_akhir=peserta_mk['nilai_akhir'],
                nilai_huruf=peserta_mk['nilai_huruf'],
            )

        return super().form_valid(form)


class PesertaMataKuliahBulkUpdateView(ProgramStudiMixin, ModelBulkUpdateView):
    form_class = PesertaMataKuliahSemesterUpdateForm
    template_name = 'mata-kuliah-semester/peserta/update-view.html'
    mk_semester_obj: MataKuliahSemester = None

    form_field_name: str = 'update_peserta'
    search_placeholder: str = 'Cari nama peserta...'
    no_choices_msg: str = 'Data peserta mata kuliah sudah sinkron dengan data di Neosia'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi

        self.choices = get_update_peserta_mk_semester_choices(self.mk_semester_obj)

        self.success_url = '{}?active_tab={}'.format(
            self.mk_semester_obj.read_detail_url(), 
            'peserta'
        )
        self.back_url = self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context
    
    def update_peserta_mk_semester(self, list_peserta_id):
        for peserta_id, peserta_data in self.choices:
            if str(peserta_id) not in list_peserta_id: continue

            new_peserta_data = peserta_data['new']

            peserta_mk_obj = PesertaMataKuliah.objects.filter(id_neosia=peserta_id)
            peserta_mk_obj.update(
                nilai_akhir=new_peserta_data['nilai_akhir'],
                nilai_huruf=new_peserta_data['nilai_huruf'],
            )
    
    def form_valid(self, form) -> HttpResponse:
        update_peserta_data = form.cleaned_data.get(self.form_field_name)

        self.update_peserta_mk_semester(update_peserta_data)
        messages.success(self.request, 'Berhasil mengupdate peserta mata kuliah semester')
        return super().form_valid(form)


class PesertaMataKuliahBulkDeleteView(ProgramStudiMixin, ModelBulkDeleteView):
    model = PesertaMataKuliah
    success_msg = 'Berhasil menghapus peserta mata kuliah semester'
    id_list_obj = 'id_peserta_mk_semester'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')

        mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

        self.program_studi_obj = mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
        self.success_url = '{}?active_tab={}'.format(
            mk_semester_obj.read_detail_url(), 
            'peserta'
        )

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id_neosia__in=self.get_list_selected_obj())
        return super().get_queryset()


# Nilai Komponen CLO Peserta
class NilaiKomponenCloEditTemplateView(FormView):
    form_class = NilaiKomponenCloPesertaFormset
    mk_semester_obj: MataKuliahSemester = None
    list_komponen_clo = None
    list_peserta_mk: list[PesertaMataKuliah] = []

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.program_studi_obj = self.mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
        self.success_url = '{}?active_tab={}'.format(
            self.mk_semester_obj.read_detail_url(), 
            'peserta'
        )

        self.list_komponen_clo = KomponenClo.objects.filter(
            clo__mk_semester=self.mk_semester_obj
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.role == 'a':
            if request.GET.get('generate') == 'true':
                messages.info(request, 'Hasil generate sudah selesai. Generate nilai hanya berlaku untuk peserta yang belum memiliki nilai di semua komponen CLO.')
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        kwargs.update({
            'list_peserta_mk': self.list_peserta_mk,
            'list_komponen_clo': self.list_komponen_clo,
            'is_generate': self.request.GET.get('generate'),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        list_form_dict = []
        form = kwargs.get('form')
        if form is None: form = self.get_form()

        list_komponen_clo_len = self.list_komponen_clo.count()

        for i, peserta in enumerate(self.list_peserta_mk):
            peserta_dict = {}
            peserta_form = []
            for j, _ in enumerate(self.list_komponen_clo):
                # Use the right increment for form index
                form_index = i + i*(list_komponen_clo_len - 1) + j
                peserta_form.append(form[form_index])
            
            peserta_dict = {
                'peserta_form': peserta_form,
                'nama': peserta.mahasiswa.nama,
                'nilai_akhir': peserta.nilai_akhir,
            }
            list_form_dict.append(peserta_dict)
        
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'back_url': self.success_url,
            'list_peserta_mk': self.list_peserta_mk,
            'list_komponen_clo': self.list_komponen_clo,
            'list_form_dict': list_form_dict,
        })
        return context


class NilaiKomponenCloEditView(ProgramStudiMixin, NilaiKomponenCloEditTemplateView):
    template_name = 'mata-kuliah-semester/nilai-komponen/edit-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

        self.list_peserta_mk = self.mk_semester_obj.get_all_peserta_mk_semester()
        super().setup(request, *args, **kwargs)
    
    def form_valid(self, form) -> HttpResponse:
        cleaned_data = form.cleaned_data
        
        for nilai_komponen_clo_submit in cleaned_data:
            # Check query first
            nilai_peserta_qs = NilaiKomponenCloPeserta.objects.filter(
                peserta=nilai_komponen_clo_submit.get('peserta'),
                komponen_clo=nilai_komponen_clo_submit.get('komponen_clo')
            )

            # If exists, then update the query
            if nilai_peserta_qs.exists():
                nilai_peserta_qs.update(**nilai_komponen_clo_submit)
            else:  # Else, create new one
                # If form is empty, skip
                if len(nilai_komponen_clo_submit.items()) == 0: continue

                # Create new one
                NilaiKomponenCloPeserta.objects.create(**nilai_komponen_clo_submit)

        messages.success(self.request, 'Proses mengedit nilai komponen CLO sudah selesai.')
        return super().form_valid(form)


class NilaiKomponenCloPesertaEditView(ProgramStudiMixin, NilaiKomponenCloEditTemplateView):
    peserta_mk_semester: PesertaMataKuliah = None

    modal_title: str = 'Edit Nilai'
    modal_content_id: str = 'edit-nilai-modal-content'
    button_text: str = 'Submit'
    success_msg: str = 'Proses mengedit nilai komponen CLO sudah selesai.'
    error_msg: str = 'Gagal mengedit nilai. Pastikan data yang anda masukkan valid.'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        peserta_id = kwargs.get('peserta_id')
        self.peserta_mk_semester = get_object_or_404(PesertaMataKuliah, id_neosia=peserta_id)
        self.mk_semester_obj = self.peserta_mk_semester.kelas_mk_semester.mk_semester

        self.list_peserta_mk = [self.peserta_mk_semester]
        super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'list_peserta_mk': self.list_peserta_mk,
            'list_komponen_clo': self.list_komponen_clo,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'modal_title': self.modal_title,
            'modal_content_id': self.modal_content_id,
            'peserta_obj': self.peserta_mk_semester,
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        cleaned_data = form.cleaned_data
        
        for nilai_komponen_clo_submit in cleaned_data:
            # Check query first
            nilai_peserta_qs = NilaiKomponenCloPeserta.objects.filter(
                peserta=self.peserta_mk_semester,
                komponen_clo=nilai_komponen_clo_submit.get('komponen_clo')
            )

            # If exists, then update the query
            if nilai_peserta_qs.exists():
                nilai_peserta_qs.update(**nilai_komponen_clo_submit)
            else:  # Else, create new one
                # If form is empty, skip
                if len(nilai_komponen_clo_submit.items()) == 0: continue

                # Create new one
                NilaiKomponenCloPeserta.objects.create(**nilai_komponen_clo_submit)

        messages.success(self.request, self.success_msg)
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        messages.error(self.request, self.error_msg)
        return super().form_invalid(form)
