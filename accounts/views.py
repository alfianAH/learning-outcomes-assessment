from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.forms import BaseForm, BaseInlineFormSet
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse, reverse_lazy
from urllib.parse import urlencode
import os
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.list_view.views import DetailWithListViewModelA
from learning_outcomes_assessment.forms.edit import (
    ModelBulkDeleteView,
    ModelBulkUpdateView
)
from learning_outcomes_assessment.forms.views import UpdateInlineFormsetView
from accounts.enums import RoleChoices
from .forms import (
    MahasiswaAuthForm,
    ProgramStudiJenjangCreateForm,
    ProgramStudiJenjangUpdateForm,
    ProgramStudiJenjangModelForm,
    ProgramStudiJenjangModelFormset,
    ProgramStudiRestrictedForm,
    ChangeUserRoleForm
)
from .models import (
    Fakultas,
    ProgramStudi,
    ProgramStudiJenjang,
    JenjangStudi
)
from .utils import (
    get_oauth_access_token,
    get_all_prodi, 
    get_update_prodi_jenjang_choices,
    validate_user
)


User = get_user_model()


# Create your views here.
def login_view(request: HttpRequest):
    form = MahasiswaAuthForm(request, data=request.POST or None)

    if form.is_valid():
        login(request, user=form.get_user())
        return redirect('/')

    context = {
        'oauth_url': reverse('accounts:oauth'),
        'form': form
    }
    return render(request, 'accounts/login.html', context=context)

def login_oauth_view(request: HttpRequest):
    MBERKAS_OAUTH_URL = 'https://mberkas.unhas.ac.id/oauth/authorize?'

    redirect_uri = os.environ.get('DJANGO_ALLOWED_HOST') + reverse('accounts:oauth-callback')
    parameters = {
        'client_id': '3',
        'redirect_uri':'https://{}'.format(redirect_uri),
        'response_type': 'code',
        'scope': '*',
    }

    return redirect('{}{}'.format(MBERKAS_OAUTH_URL, urlencode(parameters)))

def oauth_callback(request: HttpRequest):
    code = request.GET['code']
    access_token = get_oauth_access_token(code)
    
    if access_token is None:
        messages.error(request, 'Kode request tidak valid.')
        return redirect('/')
    
    user = validate_user(access_token)

    if user is None:
        messages.error(request, 'Access token tidak valid.')
        return redirect('/')
    
    is_admin = user.get('administrator') == 1
    if is_admin:
        user = authenticate(request, user=user, role=RoleChoices.ADMIN_PRODI)
    else:
        user = authenticate(request, user=user, role=RoleChoices.DOSEN)
    
    login(request, user=user)

    return redirect('/')

def logout_view(request: HttpRequest):
    logout(request)
    return redirect('/')


class ProgramStudiReadView(ProgramStudiMixin, PermissionRequiredMixin, DetailWithListViewModelA):
    permission_required = ('accounts.view_programstudi', 'accounts.view_programstudijenjang')
    single_model = ProgramStudi
    single_pk_url_kwarg = 'prodi_id'
    single_object: ProgramStudi = None

    template_name = 'accounts/prodi/home.html'
    model = ProgramStudiJenjang

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'prodi-jenjang-'
    input_name: str = 'id_prodi_jenjang'
    list_id: str = 'prodi-jenjang-list-content'
    list_custom_field_template: str = 'accounts/prodi/partials/list-custom-field-prodi-jenjang.html'
    table_custom_field_header_template: str = 'accounts/prodi/partials/table-custom-field-header-prodi-jenjang.html'
    table_custom_field_template: str = 'accounts/prodi/partials/table-custom-field-prodi-jenjang.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.program_studi_obj = self.single_object

        self.bulk_delete_url = self.single_object.get_bulk_delete_prodi_jenjang_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            program_studi=self.single_object.pk
        )
        return super().get_queryset()


class ProgramStudiCreateFormView(ProgramStudiMixin, PermissionRequiredMixin, FormView):
    permission_required = ('accounts.add_jenjangstudi', 'accounts.add_programstudijenjang', 'accounts.add_fakultas', 'accounts.change_programstudi')
    form_class = ProgramStudiJenjangCreateForm    
    template_name: str = 'accounts/prodi/create-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        prodi_id = kwargs.get('prodi_id')
        self.program_studi_obj = get_object_or_404(ProgramStudi, id_neosia=prodi_id)
        self.success_url = self.program_studi_obj.get_prodi_read_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'back_url': self.success_url
        })
        return context

    def form_valid(self, form) -> HttpResponse:
        list_prodi_jenjang_id = form.cleaned_data.get('prodi_jenjang_from_neosia')
        list_prodi_jenjang = get_all_prodi()
        
        for prodi_jenjang in list_prodi_jenjang:
            if str(prodi_jenjang['id_neosia']) not in list_prodi_jenjang_id: continue

            jenjang_studi_obj, _ = JenjangStudi.objects.get_or_create(
                **prodi_jenjang['jenjang_studi']
            )

            ProgramStudiJenjang.objects.create(
                id_neosia=prodi_jenjang['id_neosia'],
                program_studi=self.program_studi_obj,
                jenjang_studi=jenjang_studi_obj,
                nama=prodi_jenjang['nama'],
            )

            if self.program_studi_obj.fakultas is not None:
                if self.program_studi_obj.fakultas.id_neosia != prodi_jenjang['fakultas']['id_neosia']:
                    messages.warning(self.request, '{} tidak dapat ditambahkan karena merupakan bagian dari Fakultas {}. Fakultas anda: {}'.format(
                        prodi_jenjang['nama'], 
                        prodi_jenjang['fakultas']['nama'],
                        self.program_studi_obj.fakultas.nama
                    ))
                continue

            fakultas_obj, _ = Fakultas.objects.get_or_create(
                **prodi_jenjang['fakultas']
            )
            self.program_studi_obj.fakultas = fakultas_obj

        messages.success(self.request, 'Proses menambahkan jenjang program studi sudah selesai')
        
        return super().form_valid(form)


class ProgramStudiJenjangSKSBulkUpdateView(ProgramStudiMixin, PermissionRequiredMixin, UpdateInlineFormsetView):
    permission_required = ('accounts.change_programstudijenjang', )
    model = ProgramStudi
    pk_url_kwarg: str = 'prodi_id'
    template_name = 'accounts/prodi/bulk-update-sks-view.html'
    form_class = ProgramStudiJenjangModelForm
    object: ProgramStudi = None

    post_url: str = '.'
    button_text: str = 'Update'
    success_msg: str = 'Berhasil mengupdate jenjang program studi'
    error_msg: str = 'Gagal mengupdate jenjang program studi. Pastikan data yang anda masukkan valid.'

    id_total_form: str = '#id_programstudijenjang_set-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah Jenjang Program Studi'
    formset: BaseInlineFormSet = None
    formset_class: type[BaseInlineFormSet] = ProgramStudiJenjangModelFormset

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        self.program_studi_obj = self.object
        self.success_url = self.object.get_prodi_read_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_add_form"] = False
        return context
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        form = self.get_form()
        self.formset = self.formset_class(
            request.POST,
            instance=self.object
        )
        
        if self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        self.formset.save(commit=True)
        messages.success(self.request, self.success_msg)
        return redirect(self.success_url)


class ProgramStudiJenjangBulkUpdateView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkUpdateView):
    permission_required = ('accounts.change_programstudijenjang', 'accounts.change_jenjangstudi')
    form_class = ProgramStudiJenjangUpdateForm
    template_name = 'accounts/prodi/bulk-update-view.html'

    back_url: str = ''
    form_field_name: str = 'update_data_prodi_jenjang'
    search_placeholder: str = 'Cari nama jenjang prodi ...'
    submit_text: str = 'Update'
    no_choices_msg: str = 'Data jenjang prodi sudah sinkron dengan data di Neosia'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        prodi_id = kwargs.get('prodi_id')
        self.program_studi_obj = get_object_or_404(ProgramStudi, id_neosia=prodi_id)
        self.success_url = self.program_studi_obj.get_prodi_read_url()
        self.back_url = self.success_url

        self.list_prodi_jenjang_id = [prodi_jenjang['id_neosia'] for prodi_jenjang in list(self.program_studi_obj.get_prodi_jenjang().values())]
        self.choices = get_update_prodi_jenjang_choices(self.list_prodi_jenjang_id)

    def update_prodi_jenjang(self, list_prodi_jenjang_id):
        for prodi_jenjang_id, update_data in self.choices:
            if str(prodi_jenjang_id) not in list_prodi_jenjang_id: continue
            
            jenjang_studi_qs = JenjangStudi.objects.filter(id_neosia=update_data['new']['jenjang_studi']['id_neosia'])
            jenjang_studi_qs.update(**update_data['new']['jenjang_studi'])

            prodi_jenjang_qs = ProgramStudiJenjang.objects.filter(id_neosia=prodi_jenjang_id)
            prodi_jenjang_qs.update(nama=update_data['new']['nama'])

    def form_valid(self, form) -> HttpResponse:
        list_update_prodi_jenjang_id = form.cleaned_data.get(self.form_field_name)

        self.update_prodi_jenjang(list_update_prodi_jenjang_id)
        messages.success(self.request, 'Proses mengupdate prodi jenjang sudah selesai.')
        return super().form_valid(form)


class ProgramStudiJenjangBulkDeleteView(ProgramStudiMixin, PermissionRequiredMixin, ModelBulkDeleteView):
    permission_required = ('accounts.delete_programstudijenjang', )
    model = ProgramStudiJenjang
    id_list_obj = 'id_prodi_jenjang'
    success_msg = 'Berhasil menghapus jenjang program studi.'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        prodi_id = kwargs.get('prodi_id')
        self.program_studi_obj = get_object_or_404(ProgramStudi, id_neosia=prodi_id)
        self.success_url = self.program_studi_obj.get_prodi_read_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id_neosia__in=self.get_list_selected_obj())
        return super().get_queryset()


class ProgramStudiRestrictedFormView(ProgramStudiMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('accounts.change_programstudi',)
    pk_url_kwarg = 'prodi_id'
    model = ProgramStudi
    form_class = ProgramStudiRestrictedForm
    template_name: str = 'accounts/prodi/prodi-restricted-view.html'
    success_url = reverse_lazy('admin-only')

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        self.program_studi_obj = self.get_object()

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        cleaned_data = form.cleaned_data
        is_restricted_mode = cleaned_data.get('is_restricted_mode', False)

        if is_restricted_mode:
            messages.success(self.request, 'Berhasil mengaktifkan mode validasi.')
        else:
            messages.success(self.request, 'Berhasil meng-nonaktifkan mode validasi.')
        return super().form_valid(form)


class ChangeUserRoleView(FormView):
    form_class = ChangeUserRoleForm
    template_name = 'accounts/change-user-role-view.html'
    success_url = reverse_lazy('admin-only')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)
    
    def change_role(self, target_user, role, group):
        target_user.role = role
        target_user.save()
        target_user_groups = target_user.groups.all()

        # Remove from init groups
        for target_user_group in target_user_groups:
            target_user_group.user_set.remove(target_user)

        target_user.groups.add(group)
    
    def form_valid(self, form: BaseForm) -> HttpResponse:
        cleaned_data = form.cleaned_data
        username = cleaned_data.get('username')
        role = cleaned_data.get('role')
        role_str = ''
        target_user = User.objects.get(username=username)
        admin_prodi_group, _ = Group.objects.get_or_create(name='Admin Program Studi')
        dosen_group, _ = Group.objects.get_or_create(name='Dosen')
        mahasiswa_group, _ = Group.objects.get_or_create(name='Mahasiswa')

        match(role):
            case RoleChoices.ADMIN_PRODI:
                self.change_role(target_user, RoleChoices.ADMIN_PRODI, admin_prodi_group)
                role_str = RoleChoices.ADMIN_PRODI.label
            case RoleChoices.DOSEN:
                self.change_role(target_user, RoleChoices.DOSEN, dosen_group)
                role_str = RoleChoices.DOSEN.label
            case RoleChoices.MAHASISWA:
                self.change_role(target_user, RoleChoices.MAHASISWA, mahasiswa_group)
                role_str = RoleChoices.MAHASISWA.label
            case _:
                pass
        
        messages.success(self.request, 'Berhasil mengubah role user ({}) menjadi {}.'.format(username, role_str))
        return super().form_valid(form)
    
    def form_invalid(self, form) -> HttpResponse:
        messages.error(self.request, 'Gagal mengubah role.')
        return super().form_invalid(form)
