from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
from .models import(
    Semester, 
    SemesterKurikulum
)


# Create your views here.
class SemesterHomeView(ListView):
    model = SemesterKurikulum
    paginate_by: int = 10
    template_name: str = 'semester/home.html'
    # ordering: str = 'tahun_mulai'
    semester_filter = None
    semester_sort = None
