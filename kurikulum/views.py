import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView
from .models import Kurikulum
from .forms import (
    KurikulumFromNeosia,
    SemesterFromNeosia,
)
from .utils import (
    get_mata_kuliah_kurikulum,
    get_semester_by_kurikulum,
)


# Create your views here.
class KurikulumReadAllSyncFormWizardView(SessionWizardView):
    template_name: str = 'kurikulum/read-all-sync-form.html'
    form_list: list = [KurikulumFromNeosia, SemesterFromNeosia]
    latest_page: str = '0'
    revealed_page: list = []

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step)
        if step is None: step = self.steps.current
        self.update_latest_page(step)
        self.update_revealed_page(step)
        if step == '0':
            form_kwargs.update({'user': self.request.user})
        
        return form_kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        extra_data = self.storage.extra_data
        
        context['latest_page'] = extra_data.get('latest_page')
        context['revealed_page'] = extra_data.get('revealed_page')
        return context

    def update_latest_page(self, new_page: str):
        # Get latest page from storage
        extra_data = self.storage.extra_data
        self.latest_page = extra_data.get('latest_page')
        # Extra data will be none at the first time
        if self.latest_page is None: 
            # Set default value
            self.latest_page = '0'
        # Return if new page is smaller than latest page
        if int(new_page) < int(self.latest_page): return

        # Update latest page
        self.latest_page = new_page
        self.storage.extra_data.update({'latest_page': self.latest_page})

    def update_revealed_page(self, new_page: str):
        # Get latest page from storage
        extra_data = self.storage.extra_data
        revealed_page = extra_data.get('revealed_page')
        # Extra data will be none at the first time
        if revealed_page is None:
            # Set default value
            self.revealed_page = []
        else:
            # Load JSON value if there is extra data
            self.revealed_page = json.loads(revealed_page)
        # Return if new page is already in revealed page
        if new_page in self.revealed_page: return
        
        # Update revealed page
        self.revealed_page.append(new_page)
        self.storage.extra_data.update({'revealed_page': json.dumps(self.revealed_page)})
    
    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None: step = self.steps.current
        if step == '1':
            kurikulum_cleaned_data = self.get_cleaned_data_for_step('0').get('kurikulum_from_neosia')
            semester_choices = []

            for kurikulum_id in kurikulum_cleaned_data:
                semester_by_kurikulum = get_semester_by_kurikulum(kurikulum_id)
                for semester_id in semester_by_kurikulum:
                    semester_choices.append(semester_id)

            form.fields.get('semester_from_neosia').choices = semester_choices
        return form

    def done(self, form_list, **kwargs):
        success_url = reverse('kurikulum:read-all')
        return redirect(success_url)


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

