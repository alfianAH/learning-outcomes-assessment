from django.http import HttpRequest, JsonResponse
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode
import os
from .forms import MahasiswaAuthForm
from .utils import get_oauth_access_token, validate_user


# Create your views here.
def login_view(request: HttpRequest):
    form = MahasiswaAuthForm(request, data=request.POST or None)

    if form.is_valid():
        pass

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

    return JsonResponse({'access_token': user})

def logout_view(request: HttpRequest):
    logout(request)
    return redirect('/')
