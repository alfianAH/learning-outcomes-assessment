from django.http import HttpRequest, JsonResponse
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode
from requests import Request, Session
import os


# Create your views here.
def login_view(request: HttpRequest):
    context = {
        'oauth_url': reverse('accounts:oauth')
    }
    return render(request, 'accounts/login.html', context=context)

def login_oauth_view(request: HttpRequest):
    redirect_uri = os.environ.get('DJANGO_ALLOWED_HOST') + reverse('accounts:oauth-callback')
    parameters = {
        'client_id': '3',
        'redirect_uri':'http://{}'.format(redirect_uri),
        'response_type': 'code',
        'scope': '*',
    }

    print(parameters)
    # return HttpResponse()
    return redirect('https://mberkas.unhas.ac.id/oauth/authorize?{}'.format(urlencode(parameters)))

def oauth_callback(request: HttpRequest):
    code = request.GET['code']
    redirect_uri = os.environ.get('DJANGO_ALLOWED_HOST') + reverse('accounts:oauth-callback')
    parameters = {
        'grant_type': 'authorization_code',
        'client_id': '3',
        'client_secret': os.environ.get('OAUTH_CLIENT_SECRET'),
        'redirect_uri': 'http://{}'.format(redirect_uri),
        'code': code,
    }
    
    req = Request(
        'POST',
        'https://mberkas.unhas.ac.id/oauth/token',
        files={
            'grant_type': (None, parameters['grant_type']),
            'client_id': (None, parameters['client_id']),
            'client_secret': (None, parameters['client_secret']),
            'redirect_uri': (None, parameters['redirect_uri']),
            'code': (None, code),
        }
    ).prepare()
    s = Session()
    response = s.send(req)

    print("Response Status: {}".format(response.status_code))
    print("Response: {}".format(response.json()))
    
    return JsonResponse(response.json())

def logout_view(request: HttpRequest):
    logout(request)
    return redirect('/')
    