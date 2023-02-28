from django.db.models import QuerySet
from django.forms import BaseInlineFormSet
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.forms.edit import (
    ModelBulkDeleteView,
    DuplicateFormview,
)
from learning_outcomes_assessment.forms.views import (
    HtmxCreateInlineFormsetView, 
    HtmxUpdateInlineFormsetView,
    UpdateInlineFormsetView,
)
from kurikulum.models import Kurikulum
from .forms import (
    AssessmentAreaForm,
    PerformanceIndicatorAreaForm,
    PIAreaDuplicateForm,
    PerformanceIndicatorAreaFormSet,
    PerformanceIndicatorFormSet
)
from .mixins import PILockedObjectPermissionMixin
from .models import(
    AssessmentArea,
    PerformanceIndicatorArea,
    PerformanceIndicator,
)
from .utils import(
    get_kurikulum_with_pi_area,
    duplicate_pi_area_from_kurikulum_id
)


# Create your views here.
# PI Area and Assessment Area
class PIAreaCreateView(ProgramStudiMixin, PILockedObjectPermissionMixin, HtmxCreateInlineFormsetView):
    model = AssessmentArea
    form_class = AssessmentAreaForm

    modal_title: str = 'Tambah Assessment Area'
    modal_content_id: str = 'create-modal-content'
    button_text: str = 'Tambah'
    success_msg: str = 'Berhasil menambahkan assessment area dan PI area'
    error_msg: str = 'Gagal menambahkan assessment area dan PI area. Pastikan data yang anda masukkan valid.'

    id_total_form: str = '#id_performanceindicatorarea_set-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah kode area PI'
    formset_class = PerformanceIndicatorAreaFormSet
    
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        
        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)

        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        self.post_url = self.kurikulum_obj.get_create_pi_area_url()
        self.success_url = self.kurikulum_obj.read_all_pi_area_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'can_duplicate': True,
            'duplicate_url': self.kurikulum_obj.get_duplicate_pi_area_url()
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        assessment_area_obj: AssessmentArea = form.save(commit=False)
        assessment_area_obj.kurikulum = self.kurikulum_obj
        assessment_area_obj.save()

        for formset_form in self.formset:
            pi_area: PerformanceIndicatorArea = formset_form.save(commit=False)
            pi_area.assessment_area = assessment_area_obj
            pi_area.save()
        
        return super().form_valid(form)


class PIAreaUpdateView(ProgramStudiMixin, PILockedObjectPermissionMixin, HtmxUpdateInlineFormsetView):
    model = AssessmentArea
    pk_url_kwarg = 'assessment_area_id'
    form_class = AssessmentAreaForm
    object: AssessmentArea = None
    
    modal_title: str = 'Update Assessment Area'
    modal_content_id: str = 'update-modal-content'
    button_text: str = 'Update'
    success_msg: str = 'Berhasil mengupdate assessment area dan PI area'
    error_msg: str = 'Gagal mengupdate assessment area dan PI area. Pastikan data yang anda masukkan valid.'

    id_total_form: str = '#id_performanceindicatorarea_set-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah kode area PI'
    formset_class = PerformanceIndicatorAreaFormSet

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        self.post_url = self.object.get_update_pi_area_url()
        self.success_url = self.kurikulum_obj.read_all_pi_area_url()


class PIAreaReadAllView(ListView):
    model = AssessmentArea
    template_name: str = 'pi-area/home.html'
    ordering: str = 'nama'
    kurikulum_obj: Kurikulum = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = AssessmentArea.objects.filter(
            kurikulum=self.kurikulum_obj
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'input_name': 'id_pi_area',
            'prefix_id': 'pi_area-',
            'bulk_delete_url': self.kurikulum_obj.get_bulk_delete_pi_area_url(),
        })
        return context


# Assessment Area
class AssessmentAreaDeleteView(ProgramStudiMixin, PILockedObjectPermissionMixin, DeleteView):
    model = AssessmentArea
    pk_url_kwarg = 'assessment_area_id'
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        assessment_area_obj: AssessmentArea = self.get_object()
        self.success_url = assessment_area_obj.kurikulum.read_all_pi_area_url()

        self.kurikulum_obj = assessment_area_obj.kurikulum
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        return self.post(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        messages.success(self.request, 'Berhasil menghapus assessment area')
        return super().post(request, *args, **kwargs)


# PI Area
class PerformanceIndicatorAreaReadView(DetailView):
    model = PerformanceIndicatorArea
    pk_url_kwarg = 'pi_area_id'
    template_name = 'pi-area/pi-area-detail-view.html'


class PerformanceIndicatorAreaBulkDeleteView(ProgramStudiMixin, PILockedObjectPermissionMixin, ModelBulkDeleteView):
    model = PerformanceIndicatorArea
    success_msg = 'Berhasil menghapus PI Area'
    id_list_obj = 'id_pi_area'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        self.success_url = self.kurikulum_obj.read_all_pi_area_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


# PI Area and Performance Indicator
class PerformanceIndicatorAreaUpdateView(ProgramStudiMixin, PILockedObjectPermissionMixin, UpdateInlineFormsetView):
    model = PerformanceIndicatorArea
    pk_url_kwarg: str = 'pi_area_id'
    template_name = 'pi-area/peformance-indicator-area-update-view.html'
    form_class = PerformanceIndicatorAreaForm
    object: PerformanceIndicatorArea = None

    post_url: str = '.'
    button_text: str = 'Update'
    success_msg: str = 'Berhasil mengupdate PI area'
    error_msg: str = 'Gagal mengupdate PI area. Pastikan data yang anda masukkan valid.'

    id_total_form: str = '#id_performanceindicator_set-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah Performance Indicator'
    formset: BaseInlineFormSet = None
    formset_class: type[BaseInlineFormSet] = PerformanceIndicatorFormSet

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        self.success_url = self.object.read_detail_url()

        self.kurikulum_obj = self.object.assessment_area.kurikulum
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi


# Assessment area, PI Area, Performance Indicator
class PIAreaDuplicateFormView(ProgramStudiMixin, PILockedObjectPermissionMixin, DuplicateFormview):
    form_class = PIAreaDuplicateForm
    kurikulum_obj: Kurikulum = None
    empty_choices_msg = 'Kurikulum lain belum mempunyai performance indicator.'
    template_name = 'pi-area/pi-area-duplicate-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)

        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi
        self.success_url = self.kurikulum_obj.read_all_pi_area_url()
        self.choices = get_kurikulum_with_pi_area(self.kurikulum_obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'back_url': self.success_url,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'kurikulum_name': self.kurikulum_obj.nama,
        })
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        kurikulum_id = form.cleaned_data.get('kurikulum')
        duplicate_pi_area_from_kurikulum_id(kurikulum_id, self.kurikulum_obj)
        messages.success(self.request, 'Berhasil menduplikasi performance indicator ke kurikulum ini.')
        return super().form_valid(form)


class PIAreaLockAndUnlockView(ProgramStudiMixin, RedirectView):
    kurikulum_obj: Kurikulum = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.program_studi_obj = self.kurikulum_obj.prodi_jenjang.program_studi

    def get_redirect_url(self, *args, **kwargs):
        self.url = self.kurikulum_obj.read_all_pi_area_url()
        return super().get_redirect_url(*args, **kwargs)
    
    def lock_pi(self, assessment_area_qs: QuerySet[AssessmentArea]):
        is_success = True
        is_locking_success = True

        for assessment_area_obj in assessment_area_qs:
            pi_area_qs: QuerySet[PerformanceIndicatorArea] = assessment_area_obj.get_pi_area()

            for pi_area_obj in pi_area_qs:
                pi_qs: QuerySet[PerformanceIndicator] = pi_area_obj.get_performance_indicator()

                for pi_obj in pi_qs:
                    # Lock Performance Indicator
                    is_locking_success = is_locking_success and pi_obj.lock_object(self.request.user)
                    is_success = is_success and pi_obj.is_locked
                    
                # Lock Performance Indicator Area
                is_locking_success = is_locking_success and pi_area_obj.lock_object(self.request.user)
                is_success = is_success and pi_area_obj.is_locked

            # Lock assessment area
            is_locking_success = is_locking_success and assessment_area_obj.lock_object(self.request.user)
            is_success = is_success and assessment_area_obj.is_locked

        if is_success:
            self.kurikulum_obj.is_assessmentarea_locked = True
            self.kurikulum_obj.save()
        
        return is_success, is_locking_success

    def unlock_pi(self, assessment_area_qs: QuerySet[AssessmentArea]):
        is_success = True
        is_unlocking_success = True

        for assessment_area_obj in assessment_area_qs:
            pi_area_qs: QuerySet[PerformanceIndicatorArea] = assessment_area_obj.get_pi_area()

            for pi_area_obj in pi_area_qs:
                pi_qs: QuerySet[PerformanceIndicator] = pi_area_obj.get_performance_indicator()

                for pi_obj in pi_qs:
                    # Unlock Performance Indicator
                    is_unlocking_success = is_unlocking_success and pi_obj.unlock_object()
                    is_success = is_success and not pi_obj.is_locked
                    
                # Unlock Performance Indicator Area
                is_unlocking_success = is_unlocking_success and pi_area_obj.unlock_object()
                is_success = is_success and not pi_area_obj.is_locked

            # Unlock assessment area
            is_unlocking_success = is_unlocking_success and assessment_area_obj.unlock_object()
            is_success = is_success and not assessment_area_obj.is_locked

        if is_success:
            self.kurikulum_obj.is_assessmentarea_locked = False
            self.kurikulum_obj.save()
        
        return is_success, is_unlocking_success


class PIAreaLockView(PIAreaLockAndUnlockView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        assessment_area_qs: QuerySet[AssessmentArea] = self.kurikulum_obj.get_all_assessment_area()
        is_success, is_locking_success = self.lock_pi(assessment_area_qs)

        if not is_locking_success:
            messages.info(request, 'Performance Indicator sudah terkunci.')
            return super().get(request, *args, **kwargs)
            
        if is_success:
            messages.success(request, 'Berhasil mengunci Performance Indicator.')
        else:
            self.unlock_pi(assessment_area_qs)
            messages.error(request, 'Gagal mengunci Performance Indicator.')
        return super().get(request, *args, **kwargs)


class PIAreaUnlockView(PIAreaLockAndUnlockView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        assessment_area_qs: QuerySet[AssessmentArea] = self.kurikulum_obj.get_all_assessment_area()
        is_success, is_unlocking_success = self.unlock_pi(assessment_area_qs)

        if not is_unlocking_success:
            messages.info(request, 'Performance Indicator sudah tidak terkunci.')
            return super().get(request, *args, **kwargs)

        if is_success:
            messages.success(request, 'Berhasil membuka kunci Performance Indicator.')
        else:
            self.lock_pi(assessment_area_qs)
            messages.error(request, 'Gagal membuka kunci Performance Indicator.')

        return super().get(request, *args, **kwargs)
