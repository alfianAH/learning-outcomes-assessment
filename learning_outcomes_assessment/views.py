from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse


def home_view(request: HttpRequest):
    if request.user.is_authenticated:
        context = {
            "logout_url": reverse("accounts:logout"),
            "login_url": reverse("accounts:login")
        }
        return render(request, "home-view.html", context=context)
    
    return redirect(reverse("accounts:login"))
