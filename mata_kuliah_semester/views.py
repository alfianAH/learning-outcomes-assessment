import json
import os
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View, RedirectView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from accounts.enums import RoleChoices
from clo.models import KomponenClo
from learning_outcomes_assessment.auth.mixins import (
    ProgramStudiMixin,
    MahasiswaAsPesertaMixin,
    MahasiswaAndMKSemesterMixin,
)
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
    ImportNilaiUploadForm,
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
    Clo,
    NilaiCloMataKuliahSemester,
    NilaiKomponenCloPeserta,
    NilaiCloPeserta,
)
from .models import (
    MataKuliahSemester,
    NilaiExcelMataKuliahSemester,
    KelasMataKuliahSemester,
    DosenMataKuliah,
    PesertaMataKuliah,
    NilaiMataKuliahIloMahasiswa,
)
from .utils import(
    get_kelas_mk_semester,
    get_dosen_kelas_mk_semester,
    get_kelas_mk_semester_choices,
    get_update_kelas_mk_semester_choices,
    get_peserta_kelas_mk_semester,
    get_peserta_kelas_mk_semester_choices,
    get_update_peserta_mk_semester_choices,
    calculate_nilai_per_clo_mk_semester,
    calculate_nilai_per_clo_peserta,
    calculate_nilai_per_ilo_mahasiswa,
    generate_template_nilai_mk_semester,
    process_excel_file,
    generate_nilai_file,
    generate_student_performance_file,
)


# Create your views here.
class MataKuliahSemesterCreateView(ProgramStudiMixin, PermissionRequiredMixin, FormView):
    permission_required = (
        'mata_kuliah_semester.add_matakuliahsemester',
        'mata_kuliah_semester.add_kelasmatakuliahsemester',
        'mata_kuliah_semester.add_dosenmatakuliah',
    )
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

        if len(list_kelas_mk_semester_id) == 0:
            return super().form_valid(form)
        
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


class MataKuliahSemesterReadView(ProgramStudiMixin, MahasiswaAndMKSemesterMixin, PermissionRequiredMixin, DetailWithListViewModelD):
    permission_required = (
        'mata_kuliah_semester.view_matakuliahsemester',
        'mata_kuliah_semester.view_kelasmatakuliahsemester',
        'mata_kuliah_semester.view_dosenmatakuliah',
        'mata_kuliah_semester.view_pesertamatakuliah',
        'clo.view_nilaikomponenclopeserta',
        'clo.view_nilaiclomatakuliahsemester',
    )
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
    badge_template: str = 'mata-kuliah-semester/partials/peserta/badge-peserta-mk-semester.html'
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
        self.user = request.user

        self.peserta_mk_semester_qs = self.get_queryset()

        self.template_filename = '{}-{}.xlsx'.format(self.single_object.mk_kurikulum.nama, self.single_object.semester.semester.nama)
        self.nilai_filename = '{}-{}.pdf'.format(self.single_object.mk_kurikulum.nama, self.single_object.semester.semester.nama)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if 'download_template' in request.GET:
            if not request.is_ajax(): raise PermissionDenied
            return self.download_template_nilai()

        if 'download_nilai' in request.GET:
            if not request.is_ajax(): raise PermissionDenied
            return self.download_nilai()

        if self.peserta_mk_semester_qs.exists():
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
                queryset=self.peserta_mk_semester_qs
            )
            self.sort_form = PesertaMataKuliahSortForm(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[PesertaMataKuliah]:
        if self.user.role == 'm':
            self.queryset = self.model.objects.filter(
                mahasiswa=self.user,
                kelas_mk_semester__mk_semester=self.single_object
            )
        else:
            self.queryset = self.model.objects.filter(
                kelas_mk_semester__mk_semester=self.single_object
            )
        return super().get_queryset()

    def update_status_pedoman(self, status_pedoman: bool, pedoman_objects_dict: dict):
        badge_type = ''
        badge_text = ''

        if status_pedoman:
            badge_type = 'badge-success'
            badge_text = 'Sudah lengkap' if self.user.role == 'm' else 'Sudah dikunci'
        else:
            badge_type = 'badge-warning'
            badge_text = 'Belum lengkap' if self.user.role == 'm' else 'Belum dikunci'
        
        pedoman_objects_dict.update({
            'badge_type': badge_type,
            'badge_text': badge_text,
        })
    
    def pencapaian_per_clo_graph(self):
        list_nilai_clo: QuerySet[NilaiCloMataKuliahSemester] = self.single_object.get_nilai_clo_mk_semester()

        json_response = {
            'labels': [nilai_clo.clo.nama for nilai_clo in list_nilai_clo],
            'datasets': {
                'data': [nilai_clo.clo.get_total_persentase_komponen()/100 * nilai_clo.nilai for nilai_clo in list_nilai_clo],
            }
        }

        return json.dumps(json_response)
    
    def pencapaian_clo_rerata_graph(self):
        average_clo_achievement = self.single_object.average_clo_achievement
        json_response = {}

        if average_clo_achievement is None: return json.dumps(json_response)

        if average_clo_achievement > 100:
            total_exceed = average_clo_achievement - 100
            json_response.update({
                'labels': [
                    'Persentase berlebihan',
                    'Capaian CPMK rata-rata',
                ],
                'datasets': {
                    'data': [
                        total_exceed,
                        average_clo_achievement - total_exceed
                    ],
                    'backgroundColor': [
                        '#f43f5e', # Rose 500
                        '#10b981' # Emerald 500
                    ]
                }
            })
        elif average_clo_achievement == 100:
            json_response.update({
                'labels': [
                    'Capaian CPMK rata-rata',
                ],
                'datasets': {
                    'data': [
                        average_clo_achievement
                    ],
                    'backgroundColor': [
                        '#10b981' # Emerald 500
                    ]
                }
            })
        else:
            json_response.update({
                'labels': [
                    'Capaian CPMK rata-rata',
                    '-',
                ],
                'datasets': {
                    'data': [
                        average_clo_achievement,
                        100 - average_clo_achievement,
                    ],
                    'backgroundColor': [
                        '#10b981', # Emerald 500
                        '#a7f3d0' # Emerald 200
                    ]
                }
            })
        
        return json.dumps(json_response)
    
    def distribusi_nilai_huruf_graph(self):
        list_nilai = {
            'A': 0,
            'A-': 0,
            'B+': 0,
            'B': 0,
            'B-': 0,
            'C+': 0,
            'C': 0,
            'D': 0,
            'E': 0,
        }

        for peserta in self.peserta_mk_semester_qs:
            if peserta.nilai_huruf in list_nilai.keys():
                list_nilai[peserta.nilai_huruf] += 1
            else:
                if settings.DEBUG:
                    print('Nilai {} tidak ada di list nilai'.format(peserta.nilai_huruf))
        
        json_response = {
            'labels': list(list_nilai.keys()),
            'datasets': {
                'data': list(list_nilai.values()),
                'backgroundColor': [
                    '#EF4444',
                    '#F59E0B',
                    '#84CC16',
                    '#10B981',
                    '#06B6D4',
                    '#3B82F6',
                    '#8B5CF6',
                    '#D946EF',
                    '#78716C'
                ]
            }
        }

        return list_nilai, json.dumps(json_response)
    
    def download_template_nilai(self) -> HttpResponse:
        generated_template_file = generate_template_nilai_mk_semester(self.single_object, self.peserta_mk_semester_qs)
        response = FileResponse(generated_template_file, as_attachment=True, filename=self.template_filename)

        return response
    
    def download_nilai(self) -> HttpResponse:
        list_nilai_huruf = self.distribusi_nilai_huruf_graph()[0]
        nilai_file = generate_nilai_file(self.single_object, list_nilai_huruf)
        as_attachment = True
        response = FileResponse(nilai_file, as_attachment=as_attachment, filename=self.nilai_filename)

        return response

    def get_empty_komponen_clo(self):
        list_clo: QuerySet[Clo] = self.single_object.get_all_clo()
        list_komponen_clo = []

        for clo in list_clo:
            for komponen_clo in clo.get_komponen_clo():
                list_komponen_clo.append(komponen_clo)
        
        return list_komponen_clo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedoman_objects = [
            {
                'title': 'Capaian Pembelajaran Mata Kuliah (CPMK)',
                'read_detail_url': self.single_object.get_clo_read_all_url()
            },
            {
                'title': 'Rencana Pembelajaran Semester (RPS)',
                'read_detail_url': self.single_object.get_rps_home_url  ()
            }
        ]
        
        # Status Pedoman CLO
        self.update_status_pedoman(self.single_object.is_clo_locked, pedoman_objects[0])
        
        # Status pedoman RPS
        self.update_status_pedoman(self.single_object.is_rencanapembelajaransemester_locked, pedoman_objects[1])

        context.update({
            'colspan_length': 8,
            'pedoman_objects': pedoman_objects,
            'empty_komponen_clo': self.get_empty_komponen_clo(),
            'template_filename': self.template_filename,
            'nilai_filename': self.nilai_filename,
            'import_nilai_url': self.single_object.get_hx_nilai_komponen_import_url(),
            'is_not_cols_3': True,
        })

        # Show graph for admin and dosen role
        if self.user.role != 'm':
            context.update({
                'pencapaian_per_clo_graph': self.pencapaian_per_clo_graph(),
                'pencapaian_clo_rerata_graph': self.pencapaian_clo_rerata_graph(),
                'distribusi_nilai_huruf_graph': self.distribusi_nilai_huruf_graph()[1],
            })
        
        get_request = self.request.GET
        if get_request.get('active_tab') == 'hasil':
            context['is_hasil_pane'] = True

        if get_request.get('nama') or get_request.get('nilai_akhir_min') or get_request.get('nilai_akhir_max') or get_request.get(self.sort_form_ordering_by_key) or get_request.get('active_tab') == 'peserta':
            context['is_peserta_pane'] = True
        
        return context


class MataKuliahSemesterBulkDeleteView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkDeleteView):
    permission_required = (
        'mata_kuliah_semester.delete_matakuliahsemester',
    )
    model = MataKuliahSemester
    id_list_obj = 'id_mk_semester'
    success_msg = 'Berhasil mmenghapus mata kuliah semester'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        semester_prodi_id = kwargs.get('semester_prodi_id')
        semester_prodi_obj = get_object_or_404(SemesterProdi, id_neosia=semester_prodi_id)
        self.program_studi_obj = semester_prodi_obj.tahun_ajaran_prodi.prodi_jenjang.program_studi
        self.success_url = semester_prodi_obj.read_detail_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class KelasMataKuliahSemesterUpdateView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkUpdateView):
    permission_required = ('mata_kuliah_semester.change_kelasmatakuliahsemester',)
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


class KelasMataKuliahSemesterDeleteView(ProgramStudiMixin, PermissionRequiredMixin, View):
    permission_required = ('mata_kuliah_semester.delete_kelasmatakuliahsemester',)

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
class PesertaMataKuliahSemesterCreateView(ProgramStudiMixin, PermissionRequiredMixin, FormView):
    permission_required = ('mata_kuliah_semester.add_pesertamatakuliah',)
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
        if len(list_peserta_mk_semester_id) == 0:
             return super().form_valid(form)
        
        list_peserta_mk_semester = get_peserta_kelas_mk_semester(self.mk_semester_obj)
        added_peserta_number = 0

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
            added_peserta_number += 1

        messages.success(self.request, 'Berhasil menambahkan {} peserta dari {} peserta yang dipilih.'.format(added_peserta_number, len(list_peserta_mk_semester_id)))
        return super().form_valid(form)


class PesertaMataKuliahBulkUpdateView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkUpdateView):
    permission_required = ('mata_kuliah_semester.change_pesertamatakuliah',)
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


class PesertaMataKuliahBulkDeleteView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkDeleteView):
    permission_required = ('mata_kuliah_semester.delete_pesertamatakuliah',)
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


class StudentPerformanceReadView(ProgramStudiMixin, MahasiswaAsPesertaMixin, PermissionRequiredMixin, DetailView):
    permission_required = (
        'mata_kuliah_semester.view_pesertamatakuliah',
        'mata_kuliah_semester.view_nilaimatakuliahilomahasiswa',
        'clo.view_nilaiclopeserta',
    )
    model = PesertaMataKuliah
    pk_url_kwarg = 'peserta_id'
    template_name = 'mata-kuliah-semester/peserta/student-performance.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()

        self.user = self.object.mahasiswa
        self.program_studi_obj = self.object.kelas_mk_semester.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        self.filename = 'Student Performance-{}.pdf'.format(self.user.username)
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if 'download_performance' in request.GET:
            if not request.is_ajax(): raise PermissionDenied
            return self.download_student_performance()
        
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None) -> PesertaMataKuliah:
        return super().get_object(queryset)

    def download_student_performance(self) -> HttpResponse:
        nilai_file = generate_student_performance_file(self.object)
        as_attachment = True
        response = FileResponse(nilai_file, as_attachment=as_attachment, filename=self.filename)

        return response

    def perolehan_nilai_clo_graph(self):
        self.list_clo: QuerySet[Clo] = self.object.kelas_mk_semester.mk_semester.get_all_clo()
        list_nilai_clo_peserta: QuerySet[NilaiCloPeserta] = NilaiCloPeserta.objects.filter(
            clo__in=self.list_clo,
            peserta=self.object,
        )

        json_response = {
            'labels': [clo.nama for clo in self.list_clo],
            'datasets': {
                'data': [nilai_clo_peserta.nilai for nilai_clo_peserta in list_nilai_clo_peserta]
            }
        }

        return json.dumps(json_response)
    
    def perolehan_nilai_ilo_graph(self):
        self.list_nilai_ilo: QuerySet[NilaiMataKuliahIloMahasiswa] = self.object.get_nilai_ilo()
        is_radar_chart = True

        if self.list_nilai_ilo.count() <= 2:
            is_radar_chart = False
        
        json_response = {
            'labels': [nilai_ilo.ilo.nama for nilai_ilo in self.list_nilai_ilo],
            'datasets': [
                {
                    'label': 'Satisfactory Level',
                    'data': [nilai_ilo.ilo.satisfactory_level for nilai_ilo in self.list_nilai_ilo],
                    'fill': False,
                },
                {
                    'label': 'Nilai mahasiswa',
                    'data': [nilai_ilo.nilai_ilo for nilai_ilo in self.list_nilai_ilo],
                    'fill': False,
                }
            ]
        }

        return is_radar_chart, json.dumps(json_response)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_radar_chart, perolehan_nilai_ilo_graph = self.perolehan_nilai_ilo_graph()
        perolehan_nilai_clo_graph = self.perolehan_nilai_clo_graph()
        is_bar_chart_max_h_60 = self.list_clo.count() <= 5

        context.update({
            'perolehan_nilai_clo_graph': perolehan_nilai_clo_graph,
            'perolehan_nilai_ilo_graph': perolehan_nilai_ilo_graph,
            'is_radar_chart': is_radar_chart,
            'is_bar_chart_max_h_60': is_bar_chart_max_h_60,
            'list_nilai_ilo': self.list_nilai_ilo,
            'filename': self.filename,
        })
        return context
    

class StudentPerformanceCalculateView(ProgramStudiMixin, MahasiswaAsPesertaMixin, PermissionRequiredMixin, RedirectView):
    permission_required = (
        'clo.add_nilaiclopeserta',
        'clo.change_nilaiclopeserta',
        'mata_kuliah_semester.add_nilaimatakuliahilomahasiswa',
        'mata_kuliah_semester.change_nilaimatakuliahilomahasiswa',
    )
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        peserta_id = kwargs.get('peserta_id')
        self.peserta_mk = get_object_or_404(PesertaMataKuliah, id_neosia=peserta_id)
        self.user = self.peserta_mk.mahasiswa
        self.program_studi_obj = self.peserta_mk.kelas_mk_semester.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_redirect_url(self, *args, **kwargs):
        self.url = self.peserta_mk.get_student_performance_url()
        return super().get_redirect_url(*args, **kwargs)
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        mk_semester_obj = self.peserta_mk.kelas_mk_semester.mk_semester

        # If CLO is not locked or status nilai is not True, give error message
        if not mk_semester_obj.is_clo_locked or not mk_semester_obj.status_nilai:
            messages.error(request, 'Gagal menghitung student performance. Pastikan anda sudah melengkapi dan mengunci CPMK serta melengkapi nilai peserta mata kuliah.')
            return super().get(request, *args, **kwargs)
        
        calculate_nilai_per_clo_peserta(self.peserta_mk)
        calculate_nilai_per_ilo_mahasiswa(self.peserta_mk)

        messages.success(request, 'Proses perhitungan student performance sudah selesai.')
        return super().get(request, *args, **kwargs)


# Nilai Komponen CLO Peserta
class NilaiKomponenCloEditTemplateView(ProgramStudiMixin, FormView):
    form_class = NilaiKomponenCloPesertaFormset
    mk_semester_obj: MataKuliahSemester = None
    list_komponen_clo = None
    list_peserta_mk: list[PesertaMataKuliah] = []
    success_msg = 'Proses mengedit nilai komponen CPMK sudah selesai.'
    error_msg: str = 'Gagal mengedit nilai. Pastikan data yang anda masukkan valid.'
    can_generate = True

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.program_studi_obj = self.mk_semester_obj.semester.tahun_ajaran_prodi.prodi_jenjang.program_studi
        self.success_url = '{}?active_tab={}'.format(
            self.mk_semester_obj.read_detail_url(), 
            'peserta'
        )

        self.list_komponen_clo = KomponenClo.objects.filter(
            clo__mk_semester=self.mk_semester_obj
        ).order_by('clo__nama', 'instrumen_penilaian')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.mk_semester_obj.is_clo_locked:
            messages.warning(request, 'Pastikan anda sudah mengunci CPMK terlebih dahulu sebelum memasukkan nilai.')
            return redirect(self.success_url)
        
        if len(self.get_form().forms) == 0:
            messages.warning(self.request, 'Edit nilai belum bisa dilakukan. Pastikan anda sudah melengkapi CPMK dan komponen penilaiannya.')
            return redirect(self.success_url)

        if request.user.role == 'a' and self.can_generate:
            if request.GET.get('generate') == 'true':
                messages.info(request, 'Proses generate sudah selesai. Generate nilai hanya berlaku untuk peserta yang belum memiliki nilai di semua komponen CPMK.')
        
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        kwargs.update({
            'list_peserta_mk': self.list_peserta_mk,
            'list_komponen_clo': self.list_komponen_clo,
            'is_generate': self.request.GET.get('generate', '') == 'true' and self.can_generate,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get form if unvalid
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
            'can_generate': self.can_generate,
            'mk_semester_obj': self.mk_semester_obj,
            'back_url': self.success_url,
            'list_peserta_mk': self.list_peserta_mk,
            'list_komponen_clo': self.list_komponen_clo,
            'list_form_dict': list_form_dict,
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        cleaned_data = form.cleaned_data
        
        for nilai_komponen_clo_submit in cleaned_data:
            # If dict is empty, skip
            if not nilai_komponen_clo_submit: continue

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
        
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)
    
    def form_invalid(self, form) -> HttpResponse:
        messages.error(self.request, self.error_msg)
        return super().form_invalid(form)


class NilaiKomponenCloEditView(PermissionRequiredMixin, NilaiKomponenCloEditTemplateView):
    permission_required = (
        'clo.add_nilaikomponenclopeserta',
        'clo.change_nilaikomponenclopeserta',
        'mata_kuliah_semester.delete_nilaiexcelmatakuliahsemester',
        'mata_kuliah_semester.view_nilaiexcelmatakuliahsemester',
    )
    template_name = 'mata-kuliah-semester/nilai-komponen/edit-view.html'
    is_import_success = False
    message = ''
    import_result = {}

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.list_peserta_mk = self.mk_semester_obj.get_all_peserta_mk_semester()
        super().setup(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get('is_import') == 'true':
            self.can_generate = False
            # Process
            self.is_import_success, self.message, self.import_result = process_excel_file(
                self.mk_semester_obj, self.list_komponen_clo)

            if not self.is_import_success:
                messages.error(request, self.message)
                messages.warning(request, 'Pastikan anda mengunduh template nilai terbaru untuk meminimalisir error.')
                return redirect(self.success_url)
            
        return super().get(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'is_import': self.is_import_success,
            'import_result': self.import_result,
        })
        return kwargs
    
    def form_valid(self, form) -> HttpResponse:
        # If import is success, delete from database and storage
        nilai_excel_qs = NilaiExcelMataKuliahSemester.objects.filter(
            mk_semester=self.mk_semester_obj
        )
        
        if nilai_excel_qs.exists():
            if nilai_excel_qs.count() > 1:
                for nilai_excel_obj in nilai_excel_qs:
                    os.remove(nilai_excel_obj.file.path)
            else:
                os.remove(nilai_excel_qs.first().file.path)
            nilai_excel_qs.delete()
        
        return super().form_valid(form)


class NilaiKomponenCloPesertaEditView(PermissionRequiredMixin, NilaiKomponenCloEditTemplateView):
    permission_required = (
        'clo.add_nilaikomponenclopeserta',
        'clo.change_nilaikomponenclopeserta',
    )
    peserta_mk_semester: PesertaMataKuliah = None

    modal_title: str = 'Edit Nilai'
    modal_content_id: str = 'edit-nilai-modal-content'
    button_text: str = 'Submit'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        peserta_id = kwargs.get('peserta_id')
        self.peserta_mk_semester = get_object_or_404(PesertaMataKuliah, id_neosia=peserta_id)
        self.mk_semester_obj = self.peserta_mk_semester.kelas_mk_semester.mk_semester

        self.list_peserta_mk = [self.peserta_mk_semester]
        super().setup(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.htmx and not self.mk_semester_obj.is_clo_locked:
            return HttpResponse("Gagal", headers={
                'hx-redirect': self.peserta_mk_semester.get_nilai_komponen_clo_peserta_edit_url()
            })
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'modal_title': self.modal_title,
            'modal_content_id': self.modal_content_id,
            'peserta_obj': self.peserta_mk_semester,
        })
        return context


class ImportNilaiMataKuliahSemesterView(ProgramStudiMixin, PermissionRequiredMixin, FormView):
    permission_required = (
        'mata_kuliah_semester.add_nilaiexcelmatakuliahsemester',
        'mata_kuliah_semester.change_nilaiexcelmatakuliahsemester',
    )
    form_class = ImportNilaiUploadForm

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        self.success_url = '{}?is_import=true'.format(self.mk_semester_obj.get_nilai_komponen_edit_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'button_text': 'Import',
            'modal_title': 'Import Nilai',
            'modal_content_id': 'import-nilai-modal-content',
            'is_upload_file': True
        })
        return context
    
    def form_valid(self, form) -> HttpResponse:
        excel_file = form.cleaned_data.get('excel_file')
        
        nilai_excel_obj, is_created = NilaiExcelMataKuliahSemester.objects.get_or_create(
            mk_semester=self.mk_semester_obj
        )

        if not is_created:
            # If not created for the first time, remove the file first
            os.remove(nilai_excel_obj.file.path)
            nilai_excel_obj.file.delete()
        
        # Set the file
        nilai_excel_obj.file = excel_file
        # Save
        nilai_excel_obj.save()
        # Change permission
        os.chmod(nilai_excel_obj.file.path, 0o600)

        return super().form_valid(form)


# Nilai average CLO achievement
class NilaiAverageCloAchievementCalculateView(ProgramStudiMixin, PermissionRequiredMixin, RedirectView):
    permission_required = (
        'clo.add_nilaiclomatakuliahsemester',
        'clo.change_nilaiclomatakuliahsemester',
        'mata_kuliah_semester.change_matakuliahsemester',
    )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_redirect_url(self, *args, **kwargs):
        self.url = '{}?active_tab={}'.format(
            self.mk_semester_obj.read_detail_url(), 
            'hasil'
        )
        return super().get_redirect_url(*args, **kwargs)
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # If CLO is not locked or status nilai is not True, give error message
        if not self.mk_semester_obj.is_clo_locked or not self.mk_semester_obj.status_nilai:
            messages.error(request, 'Gagal menghitung capaian CPMK rata-rata. Pastikan anda sudah melengkapi dan mengunci CPMK serta melengkapi nilai peserta mata kuliah.')
            return super().get(request, *args, **kwargs)
        
        calculate_nilai_per_clo_mk_semester(self.mk_semester_obj)
        
        messages.success(request, 'Proses perhitungan capaian CPMK rata-rata sudah selesai.')
        return super().get(request, *args, **kwargs)


class NilaiAverageCloAchivementDeleteView(ProgramStudiMixin, PermissionRequiredMixin, RedirectView):
    permission_required = (
        'clo.delete_nilaiclomatakuliahsemester',
        'mata_kuliah_semester.change_matakuliahsemester',
    )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_redirect_url(self, *args, **kwargs):
        self.url = '{}?active_tab={}'.format(
            self.mk_semester_obj.read_detail_url(), 
            'hasil'
        )
        return super().get_redirect_url(*args, **kwargs)
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        list_nilai_clo_mk_semester: QuerySet[NilaiCloMataKuliahSemester] = self.mk_semester_obj.get_nilai_clo_mk_semester()
        
        list_nilai_clo_mk_semester.delete()
        self.mk_semester_obj.average_clo_achievement = None
        self.mk_semester_obj.save()
        
        messages.success(request, 'Nilai capaian per CPMK sudah dihapus.')
        return super().get(request, *args, **kwargs)
