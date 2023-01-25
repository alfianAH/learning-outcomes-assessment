import json
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.wizard.views import MySessionWizardView
from learning_outcomes_assessment.list_view.views import ListViewModelA
from learning_outcomes_assessment.forms.edit import (
    ModelBulkDeleteView,
    ModelBulkUpdateView
)
from accounts.models import ProgramStudiJenjang
from accounts.forms import ProgramStudiJenjangSelectForm
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
    get_update_kurikulum_choices
)
from mata_kuliah_kurikulum.models import MataKuliahKurikulum
from mata_kuliah_kurikulum.forms import (
    MataKuliahKurikulumCreateForm,
)
from mata_kuliah_kurikulum.utils import(
    get_mk_kurikulum,
    get_mk_kurikulum_choices,
)


# Create your views here.
class KurikulumCreateFormWizardView(MySessionWizardView):
    template_name: str = 'kurikulum/create-view.html'
    form_list: list = [ProgramStudiJenjangSelectForm, KurikulumCreateForm, MataKuliahKurikulumCreateForm]

    def get(self, request, *args, **kwargs):
        if request.user.prodi is None:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step)
        
        match step:
            case '0':
                form_kwargs.update({'user': self.request.user})
            case '1':
                selected_prodi_jenjang: int = self.get_cleaned_data_for_step('0')['prodi_jenjang']
                form_kwargs.update({
                    'prodi_jenjang_id': selected_prodi_jenjang
                })
        return form_kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        match(self.steps.current):
            case '0':
                context.update({
                    'search_text': False,
                })
            case '1':
                context.update({
                    'search_placeholder': 'Cari nama kurikulum...'
                })
            case '2':
                context.update({
                    'search_placeholder': 'Cari nama mata kuliah...'
                })
        return context

    def render_next_step(self, form, **kwargs):
        next_step = self.steps.next
        
        match(next_step):
            case '2':
                prodi_jenjang_id = self.get_cleaned_data_for_step('0')['prodi_jenjang']
                kurikulum_cleaned_data = self.get_cleaned_data_for_step('1')['kurikulum_from_neosia']
                
                mk_kurikulum_choices = []
                
                for kurikulum_id in kurikulum_cleaned_data:
                    list_mk_kurikulum = get_mk_kurikulum_choices(kurikulum_id, prodi_jenjang_id)
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
            case '2':
                self.set_form_choices(form, 'mk_kurikulum_choices', 'mk_from_neosia')
        return form

    def save_kurikulum(self, kurikulum_id: int):
        kurikulum_detail = get_detail_kurikulum(kurikulum_id)
        prodi_jenjang_id = kurikulum_detail.get('prodi_jenjang')

        # Get Program Studi Jenjang object
        prodi_jenjang_obj = ProgramStudiJenjang.objects.get(id_neosia=prodi_jenjang_id)
        kurikulum_detail.pop('prodi_jenjang')

        Kurikulum.objects.get_or_create(prodi_jenjang=prodi_jenjang_obj, **kurikulum_detail)
        return True
    
    def save_mk_kurikulum(self, list_mk_id: list[int]):
        prodi_jenjang_id = self.get_cleaned_data_for_step('0')['prodi_jenjang']
        list_kurikulum_id = self.get_cleaned_data_for_step('1')['kurikulum_from_neosia']

        for kurikulum_id in list_kurikulum_id:
            try:
                kurikulum_obj = Kurikulum.objects.get(id_neosia=kurikulum_id)
            except Kurikulum.DoesNotExist:
                messages.error(
                    self.request, 
                    'Kurikulum dengan ID: {} tidak ditemukan, sehingga gagal menyimpan mata kuliah dari kurikulum tersebut.'.format(kurikulum_id)
                )
                continue

            list_mk_kurikulum = get_mk_kurikulum(kurikulum_id, prodi_jenjang_id)
            
            for mk_kurikulum in list_mk_kurikulum:
                if str(mk_kurikulum['id_neosia']) not in list_mk_id: continue

                deleted_items = ['kurikulum']
                [mk_kurikulum.pop(item) for item in deleted_items]

                MataKuliahKurikulum.objects.create(
                    kurikulum=kurikulum_obj, 
                    **mk_kurikulum
                )

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        
        kurikulum_data = cleaned_data.get('kurikulum_from_neosia')
        mk_kurikulum_data = cleaned_data.get('mk_from_neosia')
        success_url = reverse('kurikulum:read-all')
        
        # Save kurikulum
        for kurikulum_id in kurikulum_data:
            try:
                kurikulum_id = int(kurikulum_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert Kurikulum ID ("{}") to integer'.format(kurikulum_id))
                messages.error(self.request, 'Tidak dapat mengonversi Kurikulum ID: {} ke integer'.format(kurikulum_id))
                return redirect(success_url)
            
            # If save is failed, add error message
            if not self.save_kurikulum(kurikulum_id):
                messages.error(self.request, 'Gagal menyimpan kurikulum dengan ID {}'.format(kurikulum_id))
        
        # Save mata kuliah kurikulum
        if len(mk_kurikulum_data) != 0:
            self.save_mk_kurikulum(mk_kurikulum_data)

        messages.success(self.request, 'Sinkronisasi data dari Neosia berhasil')

        return redirect(success_url)


class KurikulumBulkUpdateView(ModelBulkUpdateView):
    form_class = KurikulumBulkUpdateForm
    template_name: str = 'kurikulum/kurikulum-update-view.html'
    success_url = reverse_lazy('kurikulum:read-all')

    back_url: str = reverse_lazy('kurikulum:read-all')
    form_field_name: str = 'update_data_kurikulum'
    search_placeholder: str = 'Cari nama Kurikulum...'
    no_choices_msg: str = 'Data kurikulum sudah sinkron dengan data di Neosia'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        prodi_obj = request.user.prodi
        self.choices = get_update_kurikulum_choices(prodi_obj)

    def update_kurikulum(self, kurikulum_id: int):
        try:
            kurikulum_obj = Kurikulum.objects.filter(id_neosia=kurikulum_id)
        except Kurikulum.DoesNotExist:
            messages.error(self.request, 
                'Kurikulum dengan ID: {} tidak ditemukan, sehingga gagal mengupdate kurikulum'.format(kurikulum_id))
            return
        
        new_kurikulum_data = get_detail_kurikulum(kurikulum_id)
        kurikulum_obj.update(**new_kurikulum_data)
    
    def form_valid(self, form) -> HttpResponse:
        update_kurikulum_data = form.cleaned_data.get(self.form_field_name, [])

        # Update kurikulum
        for update_kurikulum_id, kurikulum_data in self.choices:
            new_kurikulum_data = kurikulum_data['new']

            if str(update_kurikulum_id) not in update_kurikulum_data: continue

            try:
                kurikulum_obj = Kurikulum.objects.filter(id_neosia=update_kurikulum_id)
            except Kurikulum.DoesNotExist:
                messages.error(self.request, 'Gagal mengupdate kurikulum. Error: Kurikulum dengan ID: {} tidak ditemukan.'.format(update_kurikulum_id))
                continue

            # Get prodi jenjang
            prodi_jenjang_obj: ProgramStudiJenjang = new_kurikulum_data['prodi_jenjang']

            # Update kurikulum
            kurikulum_obj.update(
                prodi_jenjang=prodi_jenjang_obj,
                nama=new_kurikulum_data['nama'],
                tahun_mulai=new_kurikulum_data['tahun_mulai'],
                is_active=new_kurikulum_data['is_active']
            )
        
        messages.success(self.request, 'Proses mengupdate kurikulum telah selesai.')
        return redirect(self.success_url)


class KurikulumReadAllView(ListViewModelA):
    """Read all Kurikulums from Program Studi X
    """
    
    model = Kurikulum
    paginate_by: int = 10
    template_name: str = 'kurikulum/home.html'
    ordering: str = ['prodi_jenjang__jenjang_studi__kode', 'tahun_mulai']
    sort_form_ordering_by_key: str = 'ordering_by'

    filter_form: KurikulumFilter = None
    sort_form: KurikulumSort = None

    bulk_delete_url: str = reverse_lazy('kurikulum:bulk-delete')
    reset_url: str = reverse_lazy('kurikulum:read-all')
    input_name: str = 'id_kurikulum'
    list_id: str = 'kurikulum-list-content'
    list_prefix_id: str = 'kurikulum-'
    badge_template: str = 'kurikulum/partials/badge-list-kurikulum.html'
    list_custom_field_template: str = 'kurikulum/partials/list-custom-field-kurikulum.html'
    table_custom_field_header_template: str = 'kurikulum/partials/table-custom-field-header-kurikulum.html'
    table_custom_field_template: str = 'kurikulum/partials/table-custom-field-kurikulum.html'
    filter_template: str = 'kurikulum/partials/kurikulum-filter-form.html'
    sort_template: str = 'kurikulum/partials/kurikulum-sort-form.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        kurikulum_qs = self.model.objects.filter(prodi_jenjang__program_studi=request.user.prodi)

        if kurikulum_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'tahun_mulai_min': request.GET.get('tahun_mulai_min', ''),
                'tahun_mulai_max': request.GET.get('tahun_mulai_max', ''),
                'is_active': request.GET.get('is_active', ''),
            }
            sort_data = {
                'ordering_by': request.GET.get('ordering_by', self.ordering[0])
            }

            self.filter_form = KurikulumFilter(
                data=filter_data or None, 
                queryset=kurikulum_qs
            )
            self.sort_form = KurikulumSort(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(prodi_jenjang__program_studi=self.request.user.prodi)

        return super().get_queryset()


class KurikulumReadView(ProgramStudiMixin, DetailView):
    model = Kurikulum
    pk_url_kwarg: str = 'kurikulum_id'
    template_name: str = 'kurikulum/detail-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object: Kurikulum = self.get_object()
        self.program_studi_obj = self.object.prodi_jenjang.program_studi


class KurikulumBulkDeleteView(ModelBulkDeleteView):
    success_url = reverse_lazy('kurikulum:read-all')
    model = Kurikulum
    id_list_obj = 'id_kurikulum'
    success_msg = 'Berhasil menghapus kurikulum'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id_neosia__in=self.get_list_selected_obj())
        return super().get_queryset()
