from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode
import os
from django.views.generic.detail import DetailView
from learning_outcomes_assessment.wizard.views import MySessionWizardView
from learning_outcomes_assessment.list_view.views import DetailWithListViewModelA
from learning_outcomes_assessment.forms.edit import ModelBulkDeleteView
from accounts.enums import RoleChoices
from .forms import (
    MahasiswaAuthForm,
    ProgramStudiJenjangForm
)
from .models import (
    ProgramStudi,
    ProgramStudiJenjang,
    JenjangStudi
)
from .utils import get_oauth_access_token, validate_user


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


class ProgramStudiReadView(DetailWithListViewModelA):
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
    # list_item_name: str = 'accounts/prodi/partials/list-item-name-prodi-jenjang.html'
    list_custom_field_template: str = 'accounts/prodi/partials/list-custom-field-prodi-jenjang.html'
    table_custom_field_header_template: str = 'accounts/prodi/partials/table-custom-field-header-prodi-jenjang.html'
    table_custom_field_template: str = 'accounts/prodi/partials/table-custom-field-prodi-jenjang.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.bulk_delete_url = self.single_object.get_bulk_delete_prodi_jenjang_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            program_studi=self.single_object.pk
        )
        return super().get_queryset()


class ProgramStudiCreateWizardFormView(MySessionWizardView):
    form_list = [ProgramStudiJenjangForm,]


class ProgramStudiBulkUpdateView(MySessionWizardView):
    form_list = [ProgramStudiJenjangForm, ]


class ProgramStudiJenjangBulkDeleteView(ModelBulkDeleteView):
    pass
