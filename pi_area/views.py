from django.http import Http404, HttpRequest, HttpResponse
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView, DeleteView

from semester.models import SemesterKurikulum
from .forms import (
    AssessmentAreaForm,
    PerformanceIndicatorAreaForm
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
    FormsetClass = None
    formset = None
    
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        self.success_url = self.semester_obj.read_all_pi_url()
        return super().setup(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        self.FormsetClass = inlineformset_factory(
            AssessmentArea, 
            PerformanceIndicatorArea, 
            form=PerformanceIndicatorAreaForm, 
            extra=0,
            can_delete=False
        )
        self.formset = self.FormsetClass()
        return super().get_form_kwargs()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'semester_obj': self.semester_obj,
            'formset': self.formset
        })
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = self.FormsetClass(request.POST)
        print('Formset: {}'.format(self.formset.is_valid()))
        print('Form: {}'.format(form.is_valid()))

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
        
        return redirect(self.success_url)


class AssessmentAreaDeleteView(DeleteView):
    model = AssessmentArea
    pk_url_kwarg = 'area_id'

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.htmx: raise Http404
        assessment_area_obj: AssessmentArea = self.get_object()
        self.success_url = assessment_area_obj.get_read_pi_url()
        
        return super().post(request, *args, **kwargs)
