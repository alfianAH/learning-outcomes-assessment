from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse


def home_view(request: HttpRequest):
    if request.user.is_authenticated:
        return render(request, 'home-view.html')
    
    return redirect(reverse('accounts:login'))
