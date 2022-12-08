from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from pi_area.models import(
    AssessmentArea,
    PerformanceIndicatorArea
)
from semester.models import SemesterKurikulum


# Create your views here.
class PerformanceIndicatorAreaReadAllView(ListView):
    model = AssessmentArea
    template_name: str = 'performance-indicator/home.html'
    ordering: str = 'nama'
    semester_obj: SemesterKurikulum = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        semester_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj = get_object_or_404(SemesterKurikulum, id=semester_id)
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'semester_obj': self.semester_obj
        })
        return context
