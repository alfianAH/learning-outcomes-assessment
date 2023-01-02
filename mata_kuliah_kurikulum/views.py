import json
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from accounts.models import ProgramStudi
from .models import MataKuliahKurikulum
from kurikulum.models import Kurikulum
from learning_outcomes_assessment.list_view.views import ListViewModelA
from mata_kuliah_kurikulum.forms import (
    MataKuliahKurikulumCreateForm,
    MataKuliahKurikulumBulkUpdateForm
)
from .filters import(
    MataKuliahKurikulumFilter,
    MataKuliahKurikulumSort
)
from mata_kuliah_kurikulum.utils import(
    get_mk_kurikulum,
    get_mk_kurikulum_choices,
)


# Create your views here.
class MataKuliahKurikulumReadAllView(ListViewModelA):
    model = MataKuliahKurikulum
    paginate_by: int = 10
    template_name: str = 'mata-kuliah-kurikulum/home.html'
    ordering: str = 'nama'
    sort_form_ordering_by_key: str = 'ordering_by'
    kurikulum_obj: Kurikulum = None

    filter_form: MataKuliahKurikulumFilter = None
    sort_form: MataKuliahKurikulumSort = None

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'mk-kurikulum-'
    input_name: str = 'id_mk_kurikulum'
    list_id: str = 'mk-kurikulum-list-content'
    list_custom_field_template: str = 'mata-kuliah-kurikulum/partials/list-custom-field-mk-kurikulum.html'
    table_custom_field_header_template: str = 'mata-kuliah-kurikulum/partials/table-custom-field-header-mk-kurikulum.html'
    table_custom_field_template: str = 'mata-kuliah-kurikulum/partials/table-custom-field-mk-kurikulum.html'
    filter_template: str = 'mata-kuliah-kurikulum/partials/mk-kurikulum-filter-form.html'
    sort_template: str = 'mata-kuliah-kurikulum/partials/mk-kurikulum-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)

        self.bulk_delete_url = self.kurikulum_obj.get_bulk_delete_mk_kurikulum_url()
        self.reset_url = self.kurikulum_obj.read_all_mk_kurikulum_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        mk_kurikulum_qs = self.get_queryset()

        if mk_kurikulum_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'sks': request.GET.get('sks', ''),
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = MataKuliahKurikulumFilter(
                data=filter_data or None,
                queryset=mk_kurikulum_qs
            )
            self.sort_form = MataKuliahKurikulumSort(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            kurikulum=self.kurikulum_obj.id_neosia
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'mk_kurikulum_create_url': self.kurikulum_obj.get_create_mk_kurikulum_url(),
            'mk_kurikulum_bulk_update_url': self.kurikulum_obj.get_bulk_update_mk_kurikulum_url(),
        })
        return context


class MataKuliahKurikulumCreateView(FormView):
    form_class = MataKuliahKurikulumCreateForm
    template_name: str = 'mata-kuliah-kurikulum/create-view.html'
    kurikulum_obj: Kurikulum = None
    prodi_id: int = None
    form_field_name: str = 'mk_from_neosia'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.success_url = self.kurikulum_obj.read_all_mk_kurikulum_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        # If there are no choices, redirect back
        if len(form.fields.get(self.form_field_name).choices) == 0:
            messages.info(request, 'Data mata kuliah kurikulum sudah sinkron dengan data di Neosia')
            return redirect(self.success_url)
        
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class = None):
        form = super().get_form(form_class)

        self.prodi_id = self.request.user.prodi.id_neosia
        mk_kurikulum_choices = get_mk_kurikulum_choices(self.kurikulum_obj.id_neosia, self.prodi_id)

        form.fields.get(self.form_field_name).choices = mk_kurikulum_choices
        
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'back_url': self.success_url
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        list_mk_id = form.cleaned_data.get(self.form_field_name)
        prodi_obj = ProgramStudi.objects.get(id_neosia=self.prodi_id)
        
        list_mk_kurikulum = get_mk_kurikulum(self.kurikulum_obj.id_neosia, self.prodi_id)
        
        for mk_kurikulum in list_mk_kurikulum:
            if str(mk_kurikulum['id_neosia']) not in list_mk_id: continue

            deleted_items = ['prodi', 'kurikulum']
            [mk_kurikulum.pop(item) for item in deleted_items]

            MataKuliahKurikulum.objects.create(
                prodi=prodi_obj, 
                kurikulum=self.kurikulum_obj, 
                **mk_kurikulum
            )
        
        messages.success(self.request, 'Berhasil menambahkan mata kuliah kurikulum')
        return redirect(self.success_url)


class MataKuliahKurikulumReadView(DetailView):
    model = MataKuliahKurikulum
    pk_url_kwarg: str = 'mk_id'
    template_name: str = 'mata-kuliah-kurikulum/detail-view.html'


class MataKuliahKurikulumBulkUpdateView(FormView):
    form_class = MataKuliahKurikulumBulkUpdateForm
    template_name: str = 'mata-kuliah-kurikulum/update-view.html'
    kurikulum_obj: Kurikulum = None
    prodi_id: int = None
    form_field_name: str = 'update_data_mk_kurikulum'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        kurikulum_id = kwargs.get('kurikulum_id')
        self.kurikulum_obj = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)
        self.prodi_id = request.user.prodi.id_neosia
        self.success_url = self.kurikulum_obj.read_all_mk_kurikulum_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()        
        kwargs['kurikulum_id'] = self.kurikulum_obj.id_neosia
        kwargs['prodi_id'] = self.prodi_id
        return kwargs

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        if len(form.fields.get(self.form_field_name).choices) == 0:
            messages.info(request, 'Data mata kuliah kurikulum sudah sinkron dengan data di Neosia')
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'kurikulum_obj': self.kurikulum_obj,
            'back_url': self.success_url,
        })
        return context

    def update_mk_kurikulum(self, list_mk_kurikulum_id: int):
        list_mk_kurikulum = get_mk_kurikulum(self.kurikulum_obj.id_neosia, self.prodi_id)
        
        for mk_kurikulum in list_mk_kurikulum:
            if str(mk_kurikulum['id_neosia']) not in list_mk_kurikulum_id: continue

            deleted_items = ['prodi', 'kurikulum']
            [mk_kurikulum.pop(item) for item in deleted_items]

            mk_kurikulum_obj = MataKuliahKurikulum.objects.filter(id_neosia=mk_kurikulum['id_neosia'])
            mk_kurikulum_obj.update(**mk_kurikulum)

    def form_valid(self, form) -> HttpResponse:
        update_mk_kurikulum_data = form.cleaned_data.get(self.form_field_name)

        self.update_mk_kurikulum(update_mk_kurikulum_data)
        messages.success(self.request, 'Berhasil mengupdate mata kuliah kurikulum')
        return super().form_valid(form)


class MataKuliahKurikulumBulkDeleteView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        kurikulum_id = kwargs.get('kurikulum_id')
        kurikulum_obj: Kurikulum = get_object_or_404(Kurikulum, id_neosia=kurikulum_id)

        list_mk_kurikulum = request.POST.getlist('id_mk_kurikulum')
        list_mk_kurikulum = [*set(list_mk_kurikulum)]

        if len(list_mk_kurikulum) > 0:
            MataKuliahKurikulum.objects.filter(id_neosia__in=list_mk_kurikulum).delete()
            messages.success(request, 'Berhasil menghapus mata kuliah kurikulum')
            
        return redirect(kurikulum_obj.read_all_mk_kurikulum_url())