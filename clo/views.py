from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.views.generic.base import View
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.list_view.views import (
    ListViewModelA, 
    DetailWithListViewModelA
)
from learning_outcomes_assessment.wizard.views import MySessionWizardView
from learning_outcomes_assessment.forms.edit import (
    ModelBulkDeleteView,
    DuplicateFormview,
)
from mata_kuliah_semester.models import MataKuliahSemester
from pi_area.models import PerformanceIndicator
from .models import (
    Clo,
    PiClo,
    KomponenClo,
)
from .forms import (
    CloForm,
    CloDuplicateForm,
    PerformanceIndicatorAreaForPiCloForm,
    PiCloForm,
    KomponenCloFormset,
)
from .utils import (
    get_semester_choices_clo_duplicate,
    duplicate_clo
)


# Create your views here.
class CloReadAllView(ProgramStudiMixin, ListViewModelA):
    template_name = 'clo/home.html'
    model = Clo
    filter_form = None
    sort_form = None
    sort_form_ordering_by_key: str = 'odering_by'
    ordering = 'nama'

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'list-clo-'
    list_id: str = 'clo-list-content'
    input_name: str = 'id_clo'
    list_custom_field_template: str = 'clo/partials/list-custom-field-clo.html'
    table_custom_field_header_template: str = 'clo/partials/table-custom-field-header-clo.html'
    table_custom_field_template: str = 'clo/partials/table-custom-field-clo.html'
    table_footer_custom_field_template: str = 'clo/partials/table-footer-custom-field-clo.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

        self.program_studi_obj =self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        
        self.bulk_delete_url = self.mk_semester_obj.get_clo_bulk_delete_url()
        self.reset_url = self.mk_semester_obj.get_clo_read_all_url()
    
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
    

class CloReadAllGraphJsonResponse(ProgramStudiMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj =self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_percentage = self.mk_semester_obj.get_total_persentase_clo()
        json_response = {
            
        }
        if total_percentage > 100:
            total_exceed = total_percentage - 100
            json_response.update({
                'labels': [
                    'Persentase berlebihan',
                    'Total Persentase CLO',
                ],
                'datasets': {
                    'data': [
                        total_exceed,
                        total_percentage - total_exceed
                    ],
                    'backgroundColor': [
                        '#f43f5e', # Rose 500
                        '#10b981' # Emerald 500
                    ]
                }
            })
        elif total_percentage == 100:
            json_response.update({
                'labels': [
                    'Total Persentase CLO',
                ],
                'datasets': {
                    'data': [
                        total_percentage
                    ],
                    'backgroundColor': [
                        '#10b981' # Emerald 500
                    ]
                }
            })
        else:
            json_response.update({
                'labels': [
                    'Total Persentase CLO',
                    'Kosong',
                ],
                'datasets': {
                    'data': [
                        total_percentage,
                        100 - total_percentage,
                    ],
                    'backgroundColor': [
                        '#10b981', # Emerald 500
                        '#a7f3d0' # Emerald 200
                    ]
                }
            })


        return JsonResponse(json_response)
    

class CloReadView(ProgramStudiMixin, DetailWithListViewModelA):
    single_model = Clo
    single_pk_url_kwarg = 'clo_id'
    single_object: Clo = None
    
    model = KomponenClo
    template_name = 'clo/detail-view.html'
    ordering = 'instrumen_penilaian'

    bulk_delete_url: str = ''
    list_prefix_id = 'komponen-clo-'
    input_name = 'id_komponen_clo'
    list_id = 'komponen-clo-list-content'
    list_item_name: str = 'clo/partials/komponen/list-item-name-komponen-clo.html'
    list_custom_field_template: str = 'clo/partials/komponen/list-custom-field-komponen-clo.html'
    table_custom_field_header_template: str = 'clo/partials/komponen/table-custom-field-header-komponen-clo.html'
    table_custom_field_template: str = 'clo/partials/komponen/table-custom-field-komponen-clo.html'
    table_footer_custom_field_template: str = 'clo/partials/komponen/table-footer-custom-field-komponen-clo.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.bulk_delete_url = self.single_object.get_komponen_clo_bulk_delete_url()

        self.program_studi_obj = self.single_object.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            clo=self.single_object
        )
        return super().get_queryset()


class CloCreateView(ProgramStudiMixin, MySessionWizardView):
    template_name: str = 'clo/create-view.html'
    form_list: list = [CloForm, PerformanceIndicatorAreaForPiCloForm, PiCloForm, KomponenCloFormset]
    mk_semester_obj: MataKuliahSemester = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.get_clo_read_all_url()
        self.program_studi_obj =self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get(self, request, *args, **kwargs):
        total_persentase = self.mk_semester_obj.get_total_persentase_clo()
        # If total_persentase is 100, no need to add anymore
        if total_persentase >= 100:
            messages.info(self.request, 'Sudah tidak bisa menambahkan CLO lagi, karena persentase CLO sudah {}%'.format(total_persentase))
            return redirect(self.success_url)

        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step)

        match(step):
            case '1':
                form_kwargs.update({
                    'kurikulum_obj': self.mk_semester_obj.mk_kurikulum.kurikulum
                })
            case '2':
                pi_area_id = self.get_cleaned_data_for_step('1').get('pi_area')
                form_kwargs.update({
                    'pi_area_id': pi_area_id
                })
            case '3':
                form_kwargs.update({
                    'mk_semester': self.mk_semester_obj
                })

        return form_kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        
        current_title = ''
        current_help_text = ''

        match(self.steps.current):
            case '0':
                current_title = 'Lengkapi Data CLO'
                current_help_text = 'Masukkan nama dan deskripsi dari CLO dari mata kuliah {0}. Untuk <b>menduplikasi CLO</b> mata kuliah <b>{0}</b> dari semester lain klik <a href="{1}">di sini</a>.'.format(self.mk_semester_obj.mk_kurikulum.nama, self.mk_semester_obj.get_clo_duplicate_url())
            case '1':
                current_title = 'Pilih ILO'
                current_help_text = 'Pilih salah satu ILO untuk mendapatkan Performance Indicator dari ILO tersebut. Performance Indicator dapat dipilih di step berikutnya.'
            case '2':
                current_title = 'Pilih Performance Indicator'
                current_help_text = 'Pilih Performance Indicator (PI) yang sesuai atau memiliki keterkaitan dengan CLO.'
            case '3':
                current_title = 'Tambahkan Komponen Penilaian'
                current_help_text = 'Tambahkan komponen penilaian pada CLO, yang terdiri dari teknik dan instrumen penilaian, dan persentasenya.<p class="text-danger">Peringatan: Jika anda meninggalkan step ini sebelum submit, maka seluruh data komponen penilaian yang diisi tidak akan tersimpan. Contoh meninggalkan step ini: pergi ke step sebelumnya atau me-refresh page.</p>'
        
        context.update({
            'current_title': current_title,
            'current_help_text': current_help_text,
            'mk_semester_obj': self.mk_semester_obj
        })
        return context
    
    def done(self, form_list, **kwargs):
        # Save CLO
        clo_form_cleaned_data = self.get_cleaned_data_for_step('0')
        clo_obj = Clo.objects.create(
            mk_semester=self.mk_semester_obj,
            **clo_form_cleaned_data
        )

        # Save PI CLO
        pi_clo_cleaned_data = self.get_cleaned_data_for_step('2').get('performance_indicator')
        for pi_clo_id in pi_clo_cleaned_data:
            try:
                performance_indicator_obj = PerformanceIndicator.objects.get(id=pi_clo_id)
            except (PerformanceIndicator.DoesNotExist, PerformanceIndicator.MultipleObjectsReturned):
                if settings.DEBUG:
                    print('Performance Indicator cannot be found. ID: {}'.format(pi_clo_id))
                continue

            PiClo.objects.create(
                performance_indicator=performance_indicator_obj,
                clo=clo_obj
            )

        # Save Komponen CLO
        komponen_clo_cleaned_data = self.get_cleaned_data_for_step('3')
        for komponen_clo_data in komponen_clo_cleaned_data:
            if komponen_clo_data.get('DELETE') is True: continue
            KomponenClo.objects.create(
                clo=clo_obj,
                teknik_penilaian=komponen_clo_data['teknik_penilaian'],
                instrumen_penilaian=komponen_clo_data['instrumen_penilaian'],
                persentase=komponen_clo_data['persentase']
            )
        
        messages.success(self.request, 'Berhasil membuat CLO dan komponen-komponennya.')

        return redirect(self.success_url)    


class CloBulkDeleteView(ProgramStudiMixin, ModelBulkDeleteView):
    model = Clo
    id_list_obj = 'id_clo'
    success_msg = 'Berhasil menghapus CLO'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        mk_semester_obj: MataKuliahSemester = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = mk_semester_obj.get_clo_read_all_url()
        self.program_studi_obj =mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class CloDuplicateView(ProgramStudiMixin, DuplicateFormview):
    form_class = CloDuplicateForm
    empty_choices_msg = 'Semester lain belum mempunyai CLO.'
    template_name = 'clo/duplicate-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj: MataKuliahSemester = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

        self.program_studi_obj =self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

        self.success_url = self.mk_semester_obj.get_clo_read_all_url()
        self.choices = get_semester_choices_clo_duplicate(self.mk_semester_obj)

    def get(self, request, *args, **kwargs):
        total_persentase = self.mk_semester_obj.get_total_persentase_clo()
        # If total_persentase is 100, no need to add anymore
        if total_persentase >= 100:
            messages.info(self.request, 'Sudah tidak bisa menambahkan CLO lagi, karena persentase CLO sudah {}%'.format(total_persentase))
            return redirect(self.success_url)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'back_url': self.success_url,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'mk_semester': self.mk_semester_obj,
        })
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        semester_prodi_id = form.cleaned_data.get('semester')
        messages.success(self.request, 'Berhasil menduplikasi CLO ke mata kuliah ini.')
        duplicate_clo(semester_prodi_id, self.mk_semester_obj)
        
        # If current duplicated percentages is more than 100, add warning message
        current_total_persentase = self.mk_semester_obj.get_total_persentase_clo()
        if current_total_persentase > 100:
            messages.warning(self.request, 'Total persentase saat ini: {}. Diharap untuk mengubah komponen CLO agar mencukupi 100%'.format(current_total_persentase))

        print(self.mk_semester_obj.get_total_persentase_clo())
        return super().form_valid(form)


# Komponen CLO
class KomponenCloBulkDeleteView(ProgramStudiMixin, ModelBulkDeleteView):
    model = KomponenClo
    id_list_obj = 'id_komponen_clo'
    success_msg = 'Berhasil menghapus komponen CLO'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        clo_id = kwargs.get('clo_id')
        clo_obj: Clo = get_object_or_404(Clo, id=clo_id)
        self.success_url = clo_obj.read_detail_url()

        self.program_studi_obj =clo_obj.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class KomponenCloCreateView():
    pass
