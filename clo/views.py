from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from learning_outcomes_assessment.list_view.views import ListViewModelA
from learning_outcomes_assessment.wizard.views import MySessionWizardView
from mata_kuliah_semester.models import MataKuliahSemester
from pi_area.models import PerformanceIndicator
from .models import (
    Clo,
    PiClo,
    KomponenClo,
)
from .forms import (
    CloForm,
    PerformanceIndicatorAreaForPiCloForm,
    PiCloForm,
    KomponenCloFormset,
)


# Create your views here.
class CloReadAllView(ListViewModelA):
    template_name = 'clo/home.html'
    model = Clo
    filter_form = None
    sort_form = None
    sort_form_ordering_by_key: str = 'odering_by'
    ordering = 'nama'

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'list-clo-'
    list_id: str = 'list-content'
    input_name: str = 'id_clo_'
    list_custom_field_template: str = 'clo/partials/list-custom-field-clo.html'
    table_custom_field_header_template: str = 'clo/partials/table-custom-field-header-clo.html'
    table_custom_field_template: str = 'clo/partials/table-custom-field-clo.html'
    filter_template: str = 'clo/partials/clo-filter-form.html'
    sort_template: str = 'clo/partials/clo-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        
        self.reset_url = self.mk_semester_obj.get_clo_read_all_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        clo_qs = self.get_queryset()

        if clo_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', '')
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

        return super().get(request, *args, **kwargs)
    
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


class CloCreateView(MySessionWizardView):
    template_name: str = 'clo/create-view.html'
    form_list: list = [CloForm, PerformanceIndicatorAreaForPiCloForm, PiCloForm, KomponenCloFormset]
    mk_semester_obj: MataKuliahSemester = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

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

        return form_kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        
        current_title = ''
        current_help_text = ''

        match(self.steps.current):
            case '0':
                current_title = 'Lengkapi Data CLO'
                current_help_text = 'Masukkan nama dan deskripsi dari CLO terkait.'
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
        cleaned_data = self.get_all_cleaned_data()
        success_url = self.mk_semester_obj.get_clo_read_all_url()

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

        return redirect(success_url)    
