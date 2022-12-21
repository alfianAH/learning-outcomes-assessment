import json
from django.forms import BaseInlineFormSet
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from learning_outcomes_assessment.forms.views import (
    HtmxCreateInlineFormsetView, 
    HtmxUpdateInlineFormsetView,
)
from semester.models import SemesterKurikulum
from .forms import (
    AssessmentAreaForm,
    PerformanceIndicatorAreaForm,
    PerformanceIndicatorAreaFormSet,
    PerformanceIndicatorFormSet
)
from .models import(
    AssessmentArea,
    PerformanceIndicatorArea
)


# Create your views here.
# PI Area and Assessment Area
class PIAreaCreateView(HtmxCreateInlineFormsetView):
    model = AssessmentArea
    form_class = AssessmentAreaForm

    modal_title: str = 'Tambah Assessment Area'
    modal_id: str = 'create-modal-content'
    button_text: str = 'Tambah'
    success_msg: str = 'Berhasil menambahkan assessment area dan PI area'
    error_msg: str = 'Gagal menambahkan assessment area dan PI area. Pastikan data yang anda masukkan valid.'

    id_total_form: str = '#id_performanceindicatorarea_set-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah kode area PI'
    formset_class = PerformanceIndicatorAreaFormSet
    
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.post_url = self.semester_obj.get_create_pi_area_url()
        self.success_url = self.semester_obj.read_all_pi_area_url()

        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'semester_obj': self.semester_obj,
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        assessment_area_obj: AssessmentArea = form.save(commit=False)
        assessment_area_obj.semester = self.semester_obj
        assessment_area_obj.save()

        for formset_form in self.formset:
            pi_area: PerformanceIndicatorArea = formset_form.save(commit=False)
            pi_area.assessment_area = assessment_area_obj
            pi_area.save()
        
        return super().form_valid(form)


class PIAreaUpdateView(HtmxUpdateInlineFormsetView):
    model = AssessmentArea
    pk_url_kwarg = 'assessment_area_id'
    form_class = AssessmentAreaForm
    object: AssessmentArea = None
    
    modal_title: str = 'Update Assessment Area'
    modal_id: str = 'update-modal-content'
    button_text: str = 'Update'
    success_msg: str = 'Berhasil mengupdate assessment area dan PI area'
    error_msg: str = 'Gagal mengupdate assessment area dan PI area. Pastikan data yang anda masukkan valid.'

    id_total_form: str = '#id_performanceindicatorarea_set-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah kode area PI'
    formset_class = PerformanceIndicatorAreaFormSet

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.post_url = self.object.get_update_pi_area_url()
        self.success_url = self.object.get_read_all_pi_area_url()


class PIAreaReadAllView(ListView):
    model = AssessmentArea
    template_name: str = 'pi-area/home.html'
    ordering: str = 'nama'
    semester_obj: SemesterKurikulum = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj = get_object_or_404(SemesterKurikulum, id=semester_id)
        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = AssessmentArea.objects.filter(
            semester=self.semester_obj
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'semester_obj': self.semester_obj,
            'input_name': 'id_pi_area',
            'prefix_id': 'pi_area-',
            'bulk_delete_url': self.semester_obj.get_bulk_delete_pi_area_url(),
        })
        return context


# Assessment Area
class AssessmentAreaDeleteView(DeleteView):
    model = AssessmentArea
    pk_url_kwarg = 'assessment_area_id'
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        assessment_area_obj: AssessmentArea = self.get_object()
        self.success_url = assessment_area_obj.get_read_all_pi_area_url()
        return self.post(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        messages.success(self.request, 'Berhasil menghapus assessment area')
        return super().post(request, *args, **kwargs)


# PI Area
class PerformanceIndicatorAreaReadView(DetailView):
    model = PerformanceIndicatorArea
    pk_url_kwarg = 'pi_area_id'
    template_name = 'pi-area/pi-area-detail-view.html'


class PerformanceIndicatorAreaBulkDeleteView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        semester_id = kwargs.get('semester_kurikulum_id')
        semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_id)

        list_pi_area = request.POST.getlist('id_pi_area')
        list_pi_area = [*set(list_pi_area)]

        if len(list_pi_area) > 0:
            PerformanceIndicatorArea.objects.filter(id__in=list_pi_area).delete()
            messages.success(self.request, 'Berhasil menghapus PI Area')
        
        return redirect(semester_obj.read_all_pi_area_url())


# PI Area and Performance Indicator
class PerformanceIndicatorAreaUpdateView(UpdateView):
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
        
        self.object: PerformanceIndicatorArea = self.get_object()
        self.success_url = self.object.read_detail_url()
        self.formset = self.formset_class(
            instance=self.object
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'button_text': self.button_text,
            'post_url': self.post_url,

            'id_total_form': self.id_total_form,
            'add_more_btn_text': self.add_more_btn_text,
            'formset': self.formset,
        })  
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = self.formset_class(
            request.POST,
            instance=self.object
        )

        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        form.save()
        self.formset.save(True)
        
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)
    
    def form_invalid(self, form) -> HttpResponse:
        form_errors = json.dumps(form.errors.as_json())
        error_message = '{}. Error: {}'.format(self.error_msg, form_errors)

        messages.error(self.request, error_message)
        return super().form_invalid(form)
