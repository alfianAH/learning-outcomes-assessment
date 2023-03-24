from django.http import HttpRequest, JsonResponse
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
from .utils import request_nusoap


def home_view(request: HttpRequest):
    if request.user.is_authenticated:
        return render(request, 'home-view.html')
    
    return redirect(reverse('accounts:login'))


def dosen_json_response(request: HttpRequest):
    search_text = request.GET.get('search', '')
    json = request_nusoap(search_text)
    
    return JsonResponse(json)
