import json
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView

from accounts.models import ProgramStudi
from .models import Kurikulum, MataKuliahKurikulum
from semester.models import (
    Semester, 
    TahunAjaran,
    TipeSemester,
    SemesterKurikulum,
)
from .filters import KurikulumFilter
from .forms import (
    KurikulumFromNeosia,
    SemesterFromNeosia,
)
from .utils import (
    get_detail_kurikulum,
    get_mata_kuliah_kurikulum,
    get_detail_semester,
    get_semester_by_kurikulum,
    get_semester_by_kurikulum_choices,
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
                semester_by_kurikulum = get_semester_by_kurikulum_choices(kurikulum_id)
                for semester_id in semester_by_kurikulum:
                    semester_choices.append(semester_id)

            form.fields.get('semester_from_neosia').choices = semester_choices
        return form

    def save_kurikulum(self, kurikulum_id: int):
        kurikulum_detail = get_detail_kurikulum(kurikulum_id)
        prodi_id = kurikulum_detail.get('prodi')
        # Get Program studi object
        prodi_obj = ProgramStudi.objects.get(id_neosia=prodi_id)
        kurikulum_detail.pop('prodi')

        Kurikulum.objects.get_or_create(prodi=prodi_obj, **kurikulum_detail)
    
    def save_mk_kurikulum(self, kurikulum_id: int):
        user_prodi_id = self.request.user.prodi.id_neosia
        list_mk_kurikulum = get_mata_kuliah_kurikulum(kurikulum_id, user_prodi_id)

        for mk_kurikulum in list_mk_kurikulum:
            kurikulum_mk_id = mk_kurikulum.get('kurikulum')
            prodi_id = mk_kurikulum.get('prodi')

            if int(kurikulum_mk_id) == kurikulum_id and int(prodi_id) == user_prodi_id:
                # Get Program studi object
                prodi_obj = ProgramStudi.objects.get(id_neosia=user_prodi_id)
                kurikulum_obj = Kurikulum.objects.get(id_neosia=kurikulum_id)
                mk_kurikulum.pop('prodi')
                mk_kurikulum.pop('kurikulum')

                mk_kurikulum_obj: MataKuliahKurikulum = MataKuliahKurikulum.objects.create(
                    prodi=prodi_obj, 
                    kurikulum=kurikulum_obj, 
                    **mk_kurikulum
                )
                mk_kurikulum_obj.save()
            else:
                # TODO: ADD MESSAGE
                if settings.DEBUG:
                    print('''Kurikulum and Prodi are not match with database. 
                    Given value: Kurikulum ID: {}, Prodi ID: {}
                    Expected value: Kurikulum ID: {}, Prodi ID: {}'''.format(
                        kurikulum_mk_id, prodi_id, 
                        kurikulum_id, user_prodi_id
                    ))
    
    def filter_semester_by_kurikulum(self, kurikulum_id: int):
        semester_by_kurikulum = get_semester_by_kurikulum(kurikulum_id)
        result = {
            kurikulum_id: semester_by_kurikulum
        }

        return result

    def save_semester(self, semester_id: int, semester_by_kurikulum: dict):
        semester_detail = get_detail_semester(semester_id)
        
        # Extract tahun ajaran
        tahun_ajaran = semester_detail.get('tahun_ajaran')
        tahun_ajaran_obj = TahunAjaran.objects.get_or_create_tahun_ajaran(tahun_ajaran)
        
        # Get tipe semester
        tipe_semester_str: str = semester_detail.get('jenis')
        match(tipe_semester_str.lower()):
            case 'ganjil':
                tipe_semester = TipeSemester.GANJIL
            case 'genap':
                tipe_semester = TipeSemester.GENAP
        
        semester_obj = Semester.objects.get_or_create(
            id_neosia = semester_detail.get('id_neosia'),
            tahun_ajaran = tahun_ajaran_obj[0],
            nama = semester_detail.get('nama'),
            tipe_semester = tipe_semester,
        )

        # Get kurikulum
        kurikulum_obj: Kurikulum = None
        for kurikulum_id, list_semester_id in semester_by_kurikulum.items():
            if semester_id not in list_semester_id: continue
            kurikulum_obj = Kurikulum.objects.get(id_neosia=kurikulum_id)
            break
        
        # If cannot get kurikulum object
        if kurikulum_obj is None:
            # Failed to save semester
            # TODO: ADD MESSAGE
            if settings.DEBUG:
                print('Cannot find Kurikulum object with Semester ID: {}'.format(semester_id))
            return False
        
        # Save semester kurikulum object
        semester_kurikulum_obj = SemesterKurikulum.objects.create(
            semester = semester_obj[0],
            kurikulum = kurikulum_obj
        )

        semester_kurikulum_obj.save()

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        
        kurikulum_data = cleaned_data.get('kurikulum_from_neosia')
        semester_by_kurikulum = {}
        semester_data = cleaned_data.get('semester_from_neosia')
        success_url = reverse('kurikulum:read-all')

        print('Kurikulum: {}'.format(kurikulum_data))
        # Save kurikulum
        for kurikulum_id in kurikulum_data:
            try:
                kurikulum_id = int(kurikulum_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert Kurikulum ID ("{}") to integer'.format(kurikulum_id))
                # TODO: ADD MESSAGE
                return redirect(success_url)
            
            self.save_kurikulum(kurikulum_id)

            # Save mata kuliah kurikulum
            self.save_mk_kurikulum(kurikulum_id)

            # Get list semester by kurikulum
            semester_by_kurikulum.update(self.filter_semester_by_kurikulum(kurikulum_id))

        # Save list semester by kurikulum
        for semester_id in semester_data:
            try:
                semester_id = int(semester_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert Semester ID ("{}") to integer'.format(semester_id))
                # TODO: ADD MESSAGE
                return redirect(success_url)
                
            self.save_semester(semester_id, semester_by_kurikulum)

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
    kurikulum_filter = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        kurikulum_qs = self.model.objects.filter(prodi=request.user.prodi)
        if kurikulum_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'tahun_mulai': request.GET.get('tahun_mulai', ''),
                'is_active': request.GET.get('is_active', ''),
            }
            self.ordering = request.GET.get('ordering_by', 'tahun_mulai')

            self.kurikulum_filter = KurikulumFilter(
                data=filter_data or None, 
                queryset=kurikulum_qs
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.kurikulum_filter is not None:
            objects = self.kurikulum_filter.qs
        else:
            objects = self.model.objects.filter(prodi=self.request.user.prodi)

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            objects = objects.order_by(*ordering)
        return objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_template'] = 'kurikulum/partials/kurikulum-filter-form.html'
        context['sort_template'] = 'kurikulum/partials/kurikulum-sort-form.html'
        context['reset_url'] = reverse('kurikulum:read-all')

        if self.kurikulum_filter is not None:
            context['filter_form'] = self.kurikulum_filter.form
            context['data_exist'] = True
        
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

