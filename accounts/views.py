from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.edit import FormView
from django.urls import reverse
from urllib.parse import urlencode
import os
from learning_outcomes_assessment.auth.mixins import ProgramStudiMixin
from learning_outcomes_assessment.wizard.views import MySessionWizardView
from learning_outcomes_assessment.list_view.views import DetailWithListViewModelA
from learning_outcomes_assessment.forms.edit import ModelBulkDeleteView
from accounts.enums import RoleChoices
from .forms import (
    MahasiswaAuthForm,
    ProgramStudiJenjangForm,
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
    validate_user
)


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
        'redirect_uri':'http://{}'.format(redirect_uri),
        'response_type': 'code',
        'scope': '*',
    }

    return redirect('{}{}'.format(MBERKAS_OAUTH_URL, urlencode(parameters)))

def oauth_callback(request: HttpRequest):
    code = request.GET['code']
    access_token = get_oauth_access_token(code)
    user = validate_user(access_token)
    print(user)
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


class ProgramStudiReadView(ProgramStudiMixin, DetailWithListViewModelA):
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


class ProgramStudiCreateFormView(ProgramStudiMixin, FormView):
    form_class = ProgramStudiJenjangForm    
    template_name: str = 'accounts/prodi/create-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        prodi_id = kwargs.get('prodi_id')
        self.program_studi_obj = get_object_or_404(ProgramStudi, id_neosia=prodi_id)
        self.success_url = self.program_studi_obj.get_prodi_read_url()

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


class ProgramStudiBulkUpdateView(FormView):
    form_list = [ProgramStudiJenjangForm, ]


class ProgramStudiJenjangBulkDeleteView(ProgramStudiMixin, ModelBulkDeleteView):
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
