from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.views.generic.base import View, RedirectView
from django.views.generic.edit import FormView
from learning_outcomes_assessment.auth.mixins import (
    ProgramStudiMixin,
    MahasiswaAndMKSemesterMixin,
)
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
from .mixins import CloLockedObjectPermissionMixin
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
class CloReadAllView(ProgramStudiMixin, MahasiswaAndMKSemesterMixin, ListViewModelA):
    template_name = 'clo/home.html'
    model = Clo
    filter_form = None
    sort_form = None
    sort_form_ordering_by_key: str = 'odering_by'

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
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_percentage = self.mk_semester_obj.get_total_persentase_clo()
        json_response = {}

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
    

class CloReadView(ProgramStudiMixin, MahasiswaAndMKSemesterMixin, DetailWithListViewModelA):
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

        self.mk_semester_obj = self.single_object.mk_semester
        self.program_studi_obj = self.single_object.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            clo=self.single_object
        )
        return super().get_queryset()


class CloCreateView(ProgramStudiMixin, CloLockedObjectPermissionMixin, MySessionWizardView):
    template_name: str = 'clo/create-view.html'
    form_list: list = [CloForm, PerformanceIndicatorAreaForPiCloForm, PiCloForm, KomponenCloFormset]
    mk_semester_obj: MataKuliahSemester = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.get_clo_read_all_url()
        self.access_denied_url = self.success_url
        self.program_studi_obj =self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get(self, request, *args, **kwargs):
        kurikulum_obj = self.mk_semester_obj.mk_kurikulum.kurikulum
        # If PI hasn't been locked, give error message
        if not kurikulum_obj.is_assessmentarea_locked:
            messages.error(request, 'Pastikan anda sudah mengunci performance indicator sebelum menambahkan CLO.')
            return redirect(self.success_url)
        
        total_persentase = self.mk_semester_obj.get_total_persentase_clo()
        # If total_persentase is 100, no need to add anymore
        if total_persentase >= 100:
            messages.info(request, 'Sudah tidak bisa menambahkan CLO lagi, karena persentase CLO sudah {}%'.format(total_persentase))
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
                    'id_total_form': '#id_{}-TOTAL_FORMS'.format(self.steps.current)
                })
        
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
        for pi_id in pi_clo_cleaned_data:
            try:
                performance_indicator_obj = PerformanceIndicator.objects.get(id=pi_id)
            except (PerformanceIndicator.DoesNotExist, PerformanceIndicator.MultipleObjectsReturned):
                if settings.DEBUG:
                    print('Performance Indicator cannot be found. ID: {}'.format(pi_id))
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


class CloUpdateView(ProgramStudiMixin, CloLockedObjectPermissionMixin, MySessionWizardView):
    form_list = [CloForm, PerformanceIndicatorAreaForPiCloForm, PiCloForm]
    template_name = 'clo/update-view.html'
    clo_obj: Clo = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        clo_id = kwargs.get('clo_id')
        self.clo_obj = get_object_or_404(Clo, id=clo_id)
        self.mk_semester_obj = self.clo_obj.mk_semester

        self.success_url = self.clo_obj.read_detail_url()
        self.program_studi_obj =self.clo_obj.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get_form_initial(self, step):
        initial = super().get_form_initial(step)

        match(step):
            case '1':
                if self.clo_obj.get_ilo() is not None:
                    initial.update({
                        'pi_area': self.clo_obj.get_ilo().pi_area.pk
                    })
            case '2':
                if self.clo_obj.get_pi_clo() is not None:
                    initial.update({
                        'performance_indicator': [pi_clo['performance_indicator_id'] for pi_clo in self.clo_obj.get_pi_clo().values()]
                    })
        return initial

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step)

        match(step):
            case '0':
                form_kwargs.update({
                    'instance': self.clo_obj,
                })
            case '1':
                form_kwargs.update({
                    'kurikulum_obj': self.clo_obj.mk_semester.mk_kurikulum.kurikulum
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
                current_help_text = 'Masukkan nama dan deskripsi dari CLO dari mata kuliah {}.'.format(self.clo_obj.mk_semester.mk_kurikulum.nama)
            case '1':
                current_title = 'Pilih ILO'
                current_help_text = 'Pilih salah satu ILO untuk mendapatkan Performance Indicator dari ILO tersebut. Performance Indicator dapat dipilih di step berikutnya.'
            case '2':
                current_title = 'Pilih Performance Indicator'
                current_help_text = 'Pilih Performance Indicator (PI) yang sesuai atau memiliki keterkaitan dengan CLO.'
        
        context.update({
            'current_title': current_title,
            'current_help_text': current_help_text,
            'clo_obj': self.clo_obj
        })
        return context
    
    def done(self, form_list, **kwargs):
        # Save CLO
        clo_obj: Clo = form_list[0].save()

        # Update PI CLO
        pi_clo_cleaned_data = self.get_cleaned_data_for_step('2').get('performance_indicator')
        pi_clo_in_db: QuerySet[PiClo] = self.clo_obj.get_pi_clo()
        pi_id_in_db = [pi_clo.performance_indicator.pk for pi_clo in pi_clo_in_db]
        
        # Create new PI CLO
        for pi_id in pi_clo_cleaned_data:
            try:
                pi_id = int(pi_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert PI CLO ID: {} to integer'.format(pi_id))
                continue
            
            # Skip creating if PI CLO is already on database
            if pi_id in pi_id_in_db: continue

            try:
                performance_indicator_obj = PerformanceIndicator.objects.get(id=pi_id)
            except (PerformanceIndicator.DoesNotExist, PerformanceIndicator.MultipleObjectsReturned):
                if settings.DEBUG:
                    print('Performance Indicator cannot be found. ID: {}'.format(pi_id))
                continue

            PiClo.objects.create(
                performance_indicator=performance_indicator_obj,
                clo=clo_obj
            )

        # Delete PI CLO if it is changed
        for pi_id in pi_id_in_db:
            # Skip deleting if PI CLO is on cleaned data
            if str(pi_id) in pi_clo_cleaned_data: continue
            
            # Delete PI CLO object 
            PiClo.objects.filter(
                performance_indicator__id=pi_id,
                clo=self.clo_obj,
            ).delete()
            

        return redirect(self.success_url)


class CloBulkDeleteView(ProgramStudiMixin, CloLockedObjectPermissionMixin, ModelBulkDeleteView):
    model = Clo
    id_list_obj = 'id_clo'
    success_msg = 'Berhasil menghapus CLO'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj: MataKuliahSemester = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.get_clo_read_all_url()
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class CloDuplicateView(ProgramStudiMixin, CloLockedObjectPermissionMixin, DuplicateFormview):
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
        is_success, message = duplicate_clo(semester_prodi_id, self.mk_semester_obj)
        self.show_clone_result_message(is_success, message)
        
        # If current duplicated percentages is more than 100, add warning message
        current_total_persentase = self.mk_semester_obj.get_total_persentase_clo()
        if current_total_persentase > 100:
            messages.warning(self.request, 'Total persentase saat ini: {}. Diharap untuk mengubah komponen CLO agar mencukupi 100%'.format(current_total_persentase))

        return super().form_valid(form)


class CloLockAndUnlockView(ProgramStudiMixin, RedirectView):
    mk_semester_obj: MataKuliahSemester = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get_redirect_url(self, *args, **kwargs):
        self.url = self.mk_semester_obj.get_clo_read_all_url()
        return super().get_redirect_url(*args, **kwargs)
    
    def lock_clo(self, clo_qs: QuerySet[Clo]):
        is_success = True
        is_locking_success = True

        for clo_obj in clo_qs:
            komponen_clo_qs: QuerySet[KomponenClo] = clo_obj.get_komponen_clo()
            pi_clo_qs: QuerySet[PiClo] = clo_obj.get_pi_clo()

            for komponen_clo_obj in komponen_clo_qs:
                # Lock komponen CLO
                is_locking_success = is_locking_success and komponen_clo_obj.lock_object(self.request.user)
                is_success = is_success and komponen_clo_obj.is_locked

            for pi_clo_obj in pi_clo_qs:
                # Lock PI CLO
                is_locking_success = is_locking_success and pi_clo_obj.lock_object(self.request.user)
                is_success = is_success and pi_clo_obj.is_locked
            
            # Lock CLO
            is_locking_success = is_locking_success and clo_obj.lock_object(self.request.user)
            is_success = is_success and clo_obj.is_locked

        if is_success:
            self.mk_semester_obj.is_clo_locked = True
            self.mk_semester_obj.save()
        
        return is_success, is_locking_success
    
    def unlock_clo(self, clo_qs: QuerySet[Clo]):
        is_success = True
        is_unlocking_success = True

        for clo_obj in clo_qs:
            komponen_clo_qs: QuerySet[KomponenClo] = clo_obj.get_komponen_clo()
            pi_clo_qs: QuerySet[PiClo] = clo_obj.get_pi_clo()

            # Unlock komponen CLO
            for komponen_clo_obj in komponen_clo_qs:
                is_unlocking_success = is_unlocking_success and komponen_clo_obj.unlock_object()
                is_success = is_success and not komponen_clo_obj.is_locked
            
            # Unlock PI CLO
            for pi_clo_obj in pi_clo_qs:
                is_unlocking_success = is_unlocking_success and pi_clo_obj.unlock_object()
                is_success = is_success and not pi_clo_obj.is_locked
            
            # Unlock CLO
            is_unlocking_success = is_unlocking_success and clo_obj.unlock_object()
            is_success = is_success and not clo_obj.is_locked

        if is_success:
            self.mk_semester_obj.is_clo_locked = False
            self.mk_semester_obj.save()

        return is_success, is_unlocking_success


class CloLockView(CloLockAndUnlockView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_persentase_clo = self.mk_semester_obj.get_total_persentase_clo()

        # Can't lock if total persentase CLO is not 100%
        if total_persentase_clo != 100: 
            messages.warning(request, 'Gagal mengunci CLO dan komponennya. Pastikan total persentase semua komponen CLO adalah 100%.')
            return super().get(request, *args, **kwargs)

        clo_qs: QuerySet[Clo] = self.mk_semester_obj.get_all_clo()
        is_success, is_locking_success = self.lock_clo(clo_qs)

        if not is_locking_success:
            messages.info(request, 'CLO dan komponennya sudah terkunci.')
            return super().get(request, *args, **kwargs)
            
        if is_success:
            messages.success(request, 'Berhasil mengunci CLO dan komponennya.')
        else:
            self.unlock_clo(clo_qs)
            messages.error(request, 'Gagal mengunci CLO dan komponennya.')
        return super().get(request, *args, **kwargs)


class CloUnlockView(CloLockAndUnlockView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        clo_qs: QuerySet[Clo] = self.mk_semester_obj.get_all_clo()
        is_success, is_unlocking_success = self.unlock_clo(clo_qs)

        if not is_unlocking_success:
            messages.info(request, 'CLO dan komponenya sudah tidak terkunci.')
            return super().get(request, *args, **kwargs)

        if is_success:
            messages.success(request, 'Berhasil membuka kunci CLO dan komponennya.')
        else:
            self.lock_clo(clo_qs)
            messages.error(request, 'Gagal membuka kunci CLO dan komponennya.')

        return super().get(request, *args, **kwargs)


# Komponen CLO
class KomponenCloBulkDeleteView(ProgramStudiMixin, CloLockedObjectPermissionMixin, ModelBulkDeleteView):
    model = KomponenClo
    id_list_obj = 'id_komponen_clo'
    success_msg = 'Berhasil menghapus komponen CLO'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        clo_id = kwargs.get('clo_id')
        self.clo_obj: Clo = get_object_or_404(Clo, id=clo_id)
        self.mk_semester_obj = self.clo_obj.mk_semester

        self.success_url = self.clo_obj.read_detail_url()

        self.program_studi_obj = self.clo_obj.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class KomponenCloCreateView(ProgramStudiMixin, CloLockedObjectPermissionMixin, FormView): 
    form_class = KomponenCloFormset
    template_name = 'clo/komponen/create-view.html'
    
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        clo_id = kwargs.get('clo_id')
        self.clo_obj: Clo = get_object_or_404(Clo, id=clo_id)
        self.mk_semester_obj = self.clo_obj.mk_semester
        
        self.program_studi_obj = self.clo_obj.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

        self.success_url = self.clo_obj.read_detail_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'clo_obj': self.clo_obj,
            'id_total_form': '#id_komponenclo_set-TOTAL_FORMS',
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.clo_obj,
            'mk_semester': self.clo_obj.mk_semester,
            'clo': self.clo_obj,
        })
        return kwargs
    
    def form_valid(self, form) -> HttpResponse:
        form.save()
        messages.success(self.request, 'Berhasil menambahkan komponen CLO.')
        return super().form_valid(form)


class KomponenCloGraphJsonResponse(ProgramStudiMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        clo_id = kwargs.get('clo_id')
        self.clo_obj = get_object_or_404(Clo, id=clo_id)
        self.program_studi_obj = self.clo_obj.mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_komponen_percentage = self.clo_obj.get_total_persentase_komponen()
        total_clo_percentage = self.clo_obj.mk_semester.get_total_persentase_clo()
        other_clo_percentage = total_clo_percentage - total_komponen_percentage

        json_response = {}

        if total_clo_percentage > 100:
            total_exceed = total_clo_percentage - 100

            json_response.update({
                'labels': [
                    'Persentase berlebihan',
                    'Persentase CLO saat ini',
                    'Persentase CLO lain',
                ],
                'datasets': {
                    'data': [
                        total_exceed,
                        total_komponen_percentage,
                        total_clo_percentage - total_exceed - total_komponen_percentage,
                    ],
                    'backgroundColor': [
                        '#f43f5e',  # Rose 500
                        '#10b981',  # Emerald 500
                        '#86efac',  # Emerald 300
                    ]
                }
            })
        elif total_clo_percentage == 100:
            json_response.update({
                'labels': [
                    'Persentase CLO saat ini',
                    'Persentase CLO lain',
                ],
                'datasets': {
                    'data': [
                        total_komponen_percentage,
                        total_clo_percentage - total_komponen_percentage,
                    ],
                    'backgroundColor': [
                        '#10b981',  # Emerald 500
                        '#86efac',  # Emerald 300
                    ]
                }
            })
        else:
            json_response.update({
                'labels': [
                    'Persentase CLO saat ini',
                    'Persentase CLO lain',
                    'Kosong',
                ],
                'datasets': {
                    'data': [
                        total_komponen_percentage,
                        total_clo_percentage - total_komponen_percentage,
                        100 - total_clo_percentage,
                    ],
                    'backgroundColor': [
                        '#10b981',  # Emerald 500
                        '#86efac',  # Emerald 300
                        '#dcfce7',  # Emerald 100
                    ]
                }
            })

        return JsonResponse(json_response)
