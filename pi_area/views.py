from django.http import Http404, HttpRequest, HttpResponse
from django.contrib import messages
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from semester.models import SemesterKurikulum
from .forms import (
    AssessmentAreaForm,
    PerformanceIndicatorAreaForm,
    PerformanceIndicatorAreaFormSet,
)
from .models import(
    AssessmentArea,
    PerformanceIndicatorArea
)


# Create your views here.
class PIAreaCreateView(CreateView):
    model = AssessmentArea
    form_class = AssessmentAreaForm
    template_name: str = 'pi-area/pi-area-create-view.html'
    formset = None
    
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.success_url = self.semester_obj.read_all_pi_area_url()

        self.formset = PerformanceIndicatorAreaFormSet()
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'id_total_form': '#id_performanceindicatorarea_set-TOTAL_FORMS',
            'add_more_btn_text': 'Tambah kode area PI',
            'semester_obj': self.semester_obj,
            'formset': self.formset
        })
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = PerformanceIndicatorAreaFormSet(request.POST)

        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        assessment_area_obj: AssessmentArea = form.save(commit=False)
        assessment_area_obj.semester = self.semester_obj
        assessment_area_obj.save()

        for formset_form in self.formset:
            pi_area: PerformanceIndicatorArea = formset_form.save(commit=False)
            pi_area.assessment_area = assessment_area_obj
            pi_area.save()

        messages.success(self.request, 'Berhasil menambahkan assessment area dan PI area')
        
        return redirect(self.success_url)


class AssessmentAreaUpdateHxView(UpdateView):
    model = AssessmentArea
    pk_url_kwarg = 'assessment_area_id'
    form_class = AssessmentAreaForm
    template_name: str = 'pi-area/partials/assessment-area-update-form.html'
    formset = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.object: AssessmentArea = self.get_object()
        self.success_url = self.object.get_read_all_pi_area_url()

        self.formset = PerformanceIndicatorAreaFormSet(
            instance=self.object
        )

    def get(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        if not request.htmx: raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'modal_title': 'Update Assessment Area',
            'modal_id': 'update-modal-content',
            'button_text': 'Update',
            'formset': self.formset,
            'id_total_form': '#id_performanceindicatorarea_set-TOTAL_FORMS',
            'post_url': self.object.get_update_assessment_area_url(),
        })
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = PerformanceIndicatorAreaFormSet(
            request.POST,
            instance=self.object,
        )

        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        assessment_area_obj: AssessmentArea = form.save()
        self.formset.save(True)

        messages.success(self.request, 'Berhasl mengupdate assessment area')

        return super().form_valid(form)


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


class PIAreaReadAllView(ListView):
    model = AssessmentArea
    template_name: str = 'pi-area/home.html'
    ordering: str = 'nama'
    semester_obj: SemesterKurikulum = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj = get_object_or_404(SemesterKurikulum, id=semester_id)
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'semester_obj': self.semester_obj,
            'input_name': 'id_pi_area',
            'prefix_id': 'pi_area-',
            'bulk_delete_url': self.semester_obj.get_bulk_delete_pi_area_url(),
        })
        return context


class PerformanceIndicatorAreaReadView(DetailView):
    pass


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

