from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import(
    DeleteView
)
from django.views.generic.list import ListView

from kurikulum.models import Kurikulum


# Create your views here.
class KurikulumReadAllSyncView(View):
    """All kurikulums synchronization from Neosia
    What to do in sync:
    1. Create Kurikulum
        1. Create Mata Kuliah Kurikulum
        2. Create Semester
            1. Create Mata Kuliah Semester
    2. Update Kurikulum
    """
    pass

class KurikulumReadSyncView(View):
    """Kurikulum synchronization from Neosia
    What to do in sync:
    1. Create Mata Kuliah Kurikulum
    2. Create Semester in Kurikulum PK
        1. Create Mata Kuliah Semester
    3. Update Semester in Kurikulum PK
    """
    pass

class KurikulumReadAllView(ListView):
    """Read all Kurikulums from Program Studi X
    """
    
    model = Kurikulum
    paginate_by: int = 10
    template_name: str = 'kurikulum/home.html'
    ordering: list[str] = ['tahun_mulai']

    def get_queryset(self):
        objects = self.model.objects.filter(prodi=self.request.user.prodi)
        return objects

    def get_context_data(self, **kwargs):
        context = {
            'read_all_sync_url': reverse('kurikulum:read-all-sync')
        }
        return context

class KurikulumReadView(DetailView):
    pass

class KurikulumDeleteView(DeleteView):
    pass


# Mata Kuliah Kurikulum

class MataKuliahKurikulumReadAllView(ListView):
    pass

class MataKuliahKurikulumReadView(DetailView):
    pass

class MataKuliahKurikulumDeleteView(DeleteView):
    pass

