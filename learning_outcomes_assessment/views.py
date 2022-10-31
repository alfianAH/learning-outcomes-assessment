from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse


def home_view(request: HttpRequest):
    if request.user.is_authenticated:
        context = {
            'kurikulum_url': reverse('kurikulum:read-all'),
            'laporan_cpl_url': '',
            'logout_url': reverse('accounts:logout'),
            'login_url': reverse('accounts:login'),
            'semester_url': '',
        }
        return render(request, 'home-view.html', context=context)
    
    return redirect(reverse('accounts:login'))
