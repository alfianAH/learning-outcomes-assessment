from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse


def home_view(request: HttpRequest):
    context = {
        "logout_url": reverse("accounts:logout"),
        "login_url": reverse("accounts:login")
    }
    return render(request, "home-view.html", context=context)
