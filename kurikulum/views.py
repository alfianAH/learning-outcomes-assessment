import json
from collections import OrderedDict
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView
from learning_outcomes_assessment.wizard.views import MySessionWizardView

from accounts.models import ProgramStudi
from .models import Kurikulum
from .filters import (
    KurikulumFilter, 
    KurikulumSort,
)
from .forms import (
    KurikulumCreateForm,
    KurikulumBulkUpdateForm,
)
from .utils import (
    get_detail_kurikulum,
)
from mata_kuliah.models import MataKuliahKurikulum
from mata_kuliah.filters import (
    MataKuliahKurikulumFilter,
    MataKuliahKurikulumSort,
)
from mata_kuliah.forms import (
    MataKuliahKurikulumCreateForm,
    MataKuliahKurikulumBulkUpdateForm
)
from mata_kuliah.utils import(
    get_mk_kurikulum,
    get_mk_kurikulum_choices,
)
from semester.models import (
    Semester, 
    TahunAjaran,
    TipeSemester,
    SemesterKurikulum,
)
from semester.filters import (
    SemesterFilter, 
    SemesterSort
)
from semester.forms import(
    SemesterKurikulumCreateForm,
    SemesterKurikulumBulkUpdateForm,
)
from semester.utils import(
    get_detail_semester,
    get_semester_by_kurikulum,
    get_semester_by_kurikulum_choices,
)


# Create your views here.
class KurikulumReadAllSyncFormWizardView(MySessionWizardView):
    template_name: str = 'kurikulum/read-all-sync-form.html'
    form_list: list = [KurikulumCreateForm, SemesterKurikulumCreateForm, MataKuliahKurikulumCreateForm]

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step)
        
        if step == '0':
            form_kwargs.update({'user': self.request.user})
        
        return form_kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        match(self.steps.current):
            case '0':
                context.update({
                    'search_placeholder': 'Cari nama kurikulum...'
                })
            case '1':
                context.update({
                    'search_placeholder': 'Cari nama semester...'
                })
            case '2':
                context.update({
                    'search_placeholder': 'Cari nama mata kuliah...'
                })
        return context

    def render_next_step(self, form, **kwargs):
        next_step = self.steps.next
        
        match(next_step): 
            case '1':
                kurikulum_cleaned_data = self.get_cleaned_data_for_step('0').get('kurikulum_from_neosia')
                semester_choices = []

                for kurikulum_id in kurikulum_cleaned_data:
                    list_semester_by_kurikulum = get_semester_by_kurikulum_choices(kurikulum_id)
                    for semester_choice in list_semester_by_kurikulum:
                        semester_choices.append(semester_choice)

                # Set extra data for semester choices
                self.storage.extra_data.update({'semester_choices': json.dumps(semester_choices)})
            case '2':
                kurikulum_cleaned_data = self.get_cleaned_data_for_step('0').get('kurikulum_from_neosia')
                prodi_id = self.request.user.prodi.id_neosia
                mk_kurikulum_choices = []
                
                for kurikulum_id in kurikulum_cleaned_data:
                    list_mk_kurikulum = get_mk_kurikulum_choices(kurikulum_id, prodi_id)
                    for mk_kurikulum_choice in list_mk_kurikulum:
                        mk_kurikulum_choices.append(mk_kurikulum_choice)

                # Set extra data for semester choices
                self.storage.extra_data.update({'mk_kurikulum_choices': json.dumps(mk_kurikulum_choices)})

        return super().render_next_step(form, **kwargs)

    def set_form_choices(self, form, choice_key: str, field_key: str):
        # Get choices from storage
        extra_data = self.storage.extra_data
        choices = extra_data.get(choice_key)

        # Extra data will be none at the first time
        if choices is None:
            # Set default value
            choices = []
        else:
            # Load JSON value if there is extra data
            choices = json.loads(choices)

        form.fields.get(field_key).choices = choices

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None: step = self.steps.current
        
        match(step):
            case '1':
                self.set_form_choices(form, 'semester_choices', 'semester_from_neosia')
            case '2':
                self.set_form_choices(form, 'mk_kurikulum_choices', 'mk_from_neosia')
        return form

    def save_kurikulum(self, kurikulum_id: int):
        kurikulum_detail = get_detail_kurikulum(kurikulum_id)
        prodi_id = kurikulum_detail.get('prodi')
        # Get Program studi object
        prodi_obj = ProgramStudi.objects.get(id_neosia=prodi_id)
        kurikulum_detail.pop('prodi')

        Kurikulum.objects.get_or_create(prodi=prodi_obj, **kurikulum_detail)
    
    def save_mk_kurikulum(self, list_mk_id: list[int]):
        list_kurikulum_id = self.get_cleaned_data_for_step('0').get('kurikulum_from_neosia')
        prodi_id = self.request.user.prodi.id_neosia
        prodi_obj = ProgramStudi.objects.get(id_neosia=prodi_id)

        for kurikulum_id in list_kurikulum_id:
            kurikulum_obj = Kurikulum.objects.get(id_neosia=kurikulum_id)

            list_mk_kurikulum = get_mk_kurikulum(kurikulum_id, prodi_id)
            
            for mk_kurikulum in list_mk_kurikulum:
                if str(mk_kurikulum['id_neosia']) not in list_mk_id: continue

                deleted_items = ['prodi', 'kurikulum']
                [mk_kurikulum.pop(item) for item in deleted_items]

                mk_kurikulum_obj: MataKuliahKurikulum = MataKuliahKurikulum.objects.create(
                    prodi=prodi_obj, 
                    kurikulum=kurikulum_obj, 
                    **mk_kurikulum
                )
                mk_kurikulum_obj.save()
    
    def filter_semester_by_kurikulum(self, kurikulum_id: int):
        semester_by_kurikulum = get_semester_by_kurikulum(kurikulum_id)
        result = {
            kurikulum_id: semester_by_kurikulum
        }

        sorted_result_by_kurikulum_id = OrderedDict(sorted(result.items()))

        return sorted_result_by_kurikulum_id

    def save_semester(self, semester_id: int, semester_by_kurikulum: dict):
        semester_detail = get_detail_semester(semester_id)
        
        # Extract tahun ajaran
        tahun_ajaran = semester_detail.get('tahun_ajaran')
        tahun_ajaran_obj = TahunAjaran.objects.get_or_create_tahun_ajaran(tahun_ajaran)
        
        # Get tipe semester
        tipe_semester_str: str = semester_detail.get('tipe_semester')
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
        for kurikulum_id, list_semester_data in semester_by_kurikulum.items():
            list_semester_id = [semester_data['id_neosia'] for semester_data in list_semester_data]
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
        mk_kurikulum_data = cleaned_data.get('mk_from_neosia')
        success_url = reverse('kurikulum:read-all')
        
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
        
        # Save mata kuliah kurikulum
        self.save_mk_kurikulum(mk_kurikulum_data)

        return redirect(success_url)


class KurikulumBulkUpdateView(FormView):
    form_class = KurikulumBulkUpdateForm
    template_name: str = 'kurikulum/kurikulum-update-view.html'
    success_url = reverse_lazy('kurikulum:read-all')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        if len(form.fields.get('update_data_kurikulum').choices) == 0:
            # TODO: ADD MESSAGE
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def update_kurikulum(self, kurikulum_id: int):
        kurikulum_obj = Kurikulum.objects.filter(id_neosia=kurikulum_id)
        new_kurikulum_data = get_detail_kurikulum(kurikulum_id)
        kurikulum_obj.update(**new_kurikulum_data)
    
    def form_valid(self, form) -> HttpResponse:
        update_kurikulum_data = form.cleaned_data.get('update_data_kurikulum', [])

        # Update kurikulum
        for kurikulum_id in update_kurikulum_data:
            try:
                kurikulum_id = int(kurikulum_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert Kurikulum ID ("{}") to integer'.format(kurikulum_id))
                # TODO: ADD MESSAGE
                return redirect(self.success_url)

            self.update_kurikulum(kurikulum_id)
        return redirect(self.success_url)


class KurikulumReadAllView(ListView):
    """Read all Kurikulums from Program Studi X
    """
    
    model = Kurikulum
    paginate_by: int = 10
    template_name: str = 'kurikulum/home.html'
    ordering: str = 'tahun_mulai'
    kurikulum_filter = None
    kurikulum_sort = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        kurikulum_qs = self.model.objects.filter(prodi=request.user.prodi)
        if kurikulum_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'tahun_mulai': request.GET.get('tahun_mulai', ''),
                'is_active': request.GET.get('is_active', ''),
            }
            sort_data = {
                'ordering_by': request.GET.get('ordering_by', self.ordering)
            }

            self.kurikulum_filter = KurikulumFilter(
                data=filter_data or None, 
                queryset=kurikulum_qs
            )
            self.kurikulum_sort = KurikulumSort(data=sort_data)

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

    def get_ordering(self):
        if self.kurikulum_sort is None:
            return super().get_ordering()
        
        if self.kurikulum_sort.is_valid():
            self.ordering = self.kurikulum_sort.cleaned_data.get('ordering_by', 'tahun_mulai')
        return super().get_ordering()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'bulk_delete_url': reverse('kurikulum:bulk-delete'),
            'filter_template': 'kurikulum/partials/kurikulum-filter-form.html',
            'sort_template': 'kurikulum/partials/kurikulum-sort-form.html',
            'reset_url': reverse('kurikulum:read-all'),
            'kurikulum_list_prefix_id': 'kurikulum-'
        })

        if self.kurikulum_filter is not None:
            context['filter_form'] = self.kurikulum_filter.form
            context['data_exist'] = True

        if self.kurikulum_sort is not None:
            context['sort_form'] = self.kurikulum_sort
        
        return context


class KurikulumReadView(DetailView):
    model = Kurikulum
    pk_url_kwarg: str = 'kurikulum_id'
    template_name: str = 'kurikulum/detail-view.html'

    mk_kurikulum_filter: MataKuliahKurikulumFilter = None
    mk_kurikulum_sort: MataKuliahKurikulumSort = None
    mk_kurikulum_ordering: str = 'nama'

    semester_filter: SemesterFilter = None
    semester_sort: SemesterSort = None
    semester_ordering: str = 'nama'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        kurikulum_obj: Kurikulum = self.get_object()
        if kurikulum_obj.prodi.id_neosia != request.user.prodi.id_neosia:
            return HttpResponse(status_code=404)

        mk_kurikulum_qs = kurikulum_obj.get_mk_kurikulum()
        semester_ids = kurikulum_obj.get_semester_ids()
        semester_qs = Semester.objects.filter(id_neosia__in=semester_ids)
        
        if mk_kurikulum_qs.exists():
            filter_data = {
                'mk_nama': request.GET.get('mk_nama', ''),
                'mk_sks': request.GET.get('mk_sks', ''),
            }
            sort_data = {
                'mk_ordering_by': request.GET.get('mk_ordering_by', self.mk_kurikulum_ordering)
            }

            self.mk_kurikulum_filter = MataKuliahKurikulumFilter(
                data=filter_data or None, 
                queryset=mk_kurikulum_qs
            )
            self.mk_kurikulum_sort = MataKuliahKurikulumSort(data=sort_data)

            if self.mk_kurikulum_sort.is_valid():
                self.mk_kurikulum_ordering = self.mk_kurikulum_sort.cleaned_data.get('mk_ordering_by', 'nama')

        if semester_qs.exists():
            filter_data = {
                'semester_nama': request.GET.get('semester_nama', ''),
                'semester_tipe_semester': request.GET.get('semester_tipe_semester', ''),
            }
            sort_data = {
                'semester_ordering_by': request.GET.get('semester_ordering_by', self.semester_ordering)
            }

            self.semester_filter = SemesterFilter(
                data=filter_data or None, 
                queryset=semester_qs
            )
            self.semester_sort = SemesterSort(data=sort_data)

            if self.semester_sort.is_valid():
                self.semester_ordering = self.semester_sort.cleaned_data.get('semester_ordering_by', 'nama')
        
        return super().get(request, *args, **kwargs)
    
    def get_objects_queryset(self, filter_form, queryset, order_by):
        if filter_form is not None:
            objects = filter_form.qs
        else:
            objects = queryset

        ordering = order_by
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            objects = objects.order_by(*ordering)
        return objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mk_objects = self.get_objects_queryset(
            self.mk_kurikulum_filter,
            self.get_object().get_mk_kurikulum(),
            self.mk_kurikulum_ordering
        )

        semester_ids = self.get_object().get_semester_ids()
        semester_qs = Semester.objects.filter(id_neosia__in=semester_ids)
        semester_objects = self.get_objects_queryset(
            self.semester_filter,
            semester_qs,
            self.semester_ordering
        )

        context.update({
            'mk_objects': mk_objects,
            'mk_filter_template': 'mata-kuliah/partials/mk-kurikulum-filter-form.html',
            'mk_sort_template': 'mata-kuliah/partials/mk-kurikulum-sort-form.html',
            'mk_list_custom_field_template': 'mata-kuliah/partials/list-custom-field-mk.html',
            'mk_table_custom_field_header_template': 'mata-kuliah/partials/table-custom-field-header-mk.html',
            'mk_table_custom_field_template': 'mata-kuliah/partials/table-custom-field-mk.html',
            'mk_prefix_id': 'mk-',
            'mk_bulk_delete_url': self.get_object().get_mk_bulk_delete(),
            
            'semester_objects': semester_objects,
            'semester_filter_template': 'semester/partials/semester-filter-form.html',
            'semester_sort_template': 'semester/partials/semester-sort-form.html',
            'semester_badge_template': 'semester/partials/badge-list-semester.html',
            'semester_list_custom_field_template': 'semester/partials/list-custom-field-semester.html',
            'semester_table_custom_field_header_template': 'semester/partials/table-custom-field-header-semester.html',
            'semester_table_custom_field_template': 'semester/partials/table-custom-field-semester.html',
            'semester_prefix_id': 'semester-',
            'semester_bulk_delete_url': self.get_object().get_semester_bulk_delete(),
            
            'reset_url': self.get_object().read_detail_url()
        })

        if self.mk_kurikulum_filter is not None:
            context['mk_data_exist'] = True
            context['mk_filter_form'] = self.mk_kurikulum_filter.form
        if self.mk_kurikulum_sort is not None:
            context['mk_sort_form'] = self.mk_kurikulum_sort
        
        if self.semester_filter is not None:
            context['semester_data_exist'] = True
            context['semester_filter_form'] = self.semester_filter.form
        if self.semester_sort is not None:
            context['semester_sort_form'] = self.semester_sort

        return context


class KurikulumBulkDeleteView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        list_kurikulum = request.POST.getlist('id_kurikulum')
        list_kurikulum = [*set(list_kurikulum)]

        if len(list_kurikulum) > 0:
            Kurikulum.objects.filter(id_neosia__in=list_kurikulum).delete()
            
        return redirect(reverse('kurikulum:read-all'))


# Mata Kuliah Kurikulum
class MataKuliahKurikulumCreateView(FormView):
    form_class = MataKuliahKurikulumCreateForm
    template_name: str = 'mata-kuliah/mk-kurikulum-create-view.html'
    kurikulum_id: int = None
    prodi_id: int = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        # If there are no choices, redirect back
        if len(form.fields.get('mk_from_neosia').choices) == 0:
            # TODO: ADD MESSAGE
            return redirect(self.success_url)
        
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        
        self.kurikulum_id = self.kwargs.get('kurikulum_id')
        self.success_url = reverse('kurikulum:read', kwargs={
            'kurikulum_id': self.kurikulum_id
        })

        self.prodi_id = self.request.user.prodi.id_neosia

        mk_kurikulum_choices = get_mk_kurikulum_choices(self.kurikulum_id, self.prodi_id)

        form.fields.get('mk_from_neosia').choices = mk_kurikulum_choices
        
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_id': self.kurikulum_id
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        list_mk_id = form.cleaned_data.get('mk_from_neosia')
        kurikulum_obj = Kurikulum.objects.get(id_neosia=self.kurikulum_id)
        prodi_obj = ProgramStudi.objects.get(id_neosia=self.prodi_id)
        
        list_mk_kurikulum = get_mk_kurikulum(self.kurikulum_id, self.prodi_id)
        
        for mk_kurikulum in list_mk_kurikulum:
            if str(mk_kurikulum['id_neosia']) not in list_mk_id: continue

            deleted_items = ['prodi', 'kurikulum']
            [mk_kurikulum.pop(item) for item in deleted_items]

            mk_kurikulum_obj: MataKuliahKurikulum = MataKuliahKurikulum.objects.create(
                prodi=prodi_obj, 
                kurikulum=kurikulum_obj, 
                **mk_kurikulum
            )
            mk_kurikulum_obj.save()
        
        return redirect(self.success_url)


class MataKuliahKurikulumReadView(DetailView):
    pass


class MataKuliahKurikulumUpdateView(FormView):
    form_class = MataKuliahKurikulumBulkUpdateForm
    template_name: str = 'mata-kuliah/mk-kurikulum-update-view.html'
    kurikulum_id: int = None
    prodi_id: int = None

    def get_form(self, form_class = None):
        self.kurikulum_id = self.kwargs.get('kurikulum_id')
        self.prodi_id = self.request.user.prodi.id_neosia
        self.success_url = reverse('kurikulum:read', kwargs={
            'kurikulum_id': self.kurikulum_id
        })
        
        return super().get_form(form_class)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()        
        kwargs['kurikulum_id'] = self.kurikulum_id
        kwargs['prodi_id'] = self.prodi_id
        return kwargs

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        if len(form.fields.get('update_data_mk_kurikulum').choices) == 0:
            # TODO: ADD MESSAGE
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_id': self.kurikulum_id
        })
        return context

    def update_mk_kurikulum(self, list_mk_kurikulum_id: int):
        list_mk_kurikulum = get_mk_kurikulum(self.kurikulum_id, self.prodi_id)
        
        for mk_kurikulum in list_mk_kurikulum:
            if str(mk_kurikulum['id_neosia']) not in list_mk_kurikulum_id: continue

            deleted_items = ['prodi', 'kurikulum']
            [mk_kurikulum.pop(item) for item in deleted_items]

            mk_kurikulum_obj = MataKuliahKurikulum.objects.filter(id_neosia=mk_kurikulum['id_neosia'])
            mk_kurikulum_obj.update(**mk_kurikulum)

    def form_valid(self, form) -> HttpResponse:
        update_mk_kurikulum_data = form.cleaned_data.get('update_data_mk_kurikulum')

        self.update_mk_kurikulum(update_mk_kurikulum_data)
        
        return super().form_valid(form)


class MataKuliahKurikulumBulkDeleteView(DeleteView):
    model = Kurikulum
    pk_url_kwarg: str = 'kurikulum_id'

    def post(self, request: HttpRequest, *args, **kwargs):
        list_mk_kurikulum = request.POST.getlist('id_mk_kurikulum')
        list_mk_kurikulum = [*set(list_mk_kurikulum)]

        if len(list_mk_kurikulum) > 0:
            MataKuliahKurikulum.objects.filter(id_neosia__in=list_mk_kurikulum).delete()
            
        return redirect(self.get_object().read_detail_url())


# Semester Kurikulum
class SemesterKurikulumCreateView(FormView):
    form_class = SemesterKurikulumCreateForm
    template_name: str = 'semester/semester-kurikulum-create-view.html'
    kurikulum_id: int = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        # If there are no choices, redirect back
        if len(form.fields.get('semester_from_neosia').choices) == 0:
            # TODO: ADD MESSAGE
            return redirect(self.success_url)
        
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        self.kurikulum_id = self.kwargs.get('kurikulum_id')
        self.success_url = reverse('kurikulum:read', kwargs={
            'kurikulum_id': self.kurikulum_id
        })

        semester_choices = get_semester_by_kurikulum_choices(self.kurikulum_id)
        print(semester_choices)

        form.fields.get('semester_from_neosia').choices = semester_choices

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_id': self.kurikulum_id
        })
        return context

    def save_semester(self, semester_id: int):
        semester_detail = get_detail_semester(semester_id)
        
        # Extract tahun ajaran
        tahun_ajaran = semester_detail.get('tahun_ajaran')
        tahun_ajaran_obj = TahunAjaran.objects.get_or_create_tahun_ajaran(tahun_ajaran)
        
        # Get tipe semester
        tipe_semester_str: str = semester_detail.get('tipe_semester')
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
        kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=self.kurikulum_id)
        
        # Save semester kurikulum object
        semester_kurikulum_obj = SemesterKurikulum.objects.create(
            semester = semester_obj[0],
            kurikulum = kurikulum_obj
        )

        semester_kurikulum_obj.save()

    def form_valid(self, form) -> HttpResponse:
        list_semester_id = form.cleaned_data.get('semester_from_neosia')

        for semester_id in list_semester_id:
            try:
                semester_id = int(semester_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert Semester ID ("{}") to integer'.format(semester_id))
                # TODO: ADD MESSAGE
                return redirect(self.success_url)
                
            self.save_semester(semester_id)
        
        return super().form_valid(form)


class SemesterKurikulumUpdateView(FormView):
    pass


class SemesterKurikulumBulkDeleteView(DeleteView):
    model = Kurikulum
    pk_url_kwarg: str = 'kurikulum_id'

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        kurikulum_obj: Kurikulum = self.get_object()
        kurikulum_id = kurikulum_obj.id_neosia
        list_semester_kurikulum = request.POST.getlist('id_semester')
        list_semester_kurikulum = [*set(list_semester_kurikulum)]

        if len(list_semester_kurikulum) > 0:
            print(list_semester_kurikulum)
            SemesterKurikulum.objects.filter(semester__in=list_semester_kurikulum, kurikulum=kurikulum_id).delete()
            
        return redirect(self.get_object().read_detail_url())
