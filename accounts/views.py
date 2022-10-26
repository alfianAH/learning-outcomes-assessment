from django.http import HttpRequest
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from .forms import MyAuthForm


# Create your views here.
def login_view(request: HttpRequest):
    form = MyAuthForm(request, data=request.POST or None)

    if form.is_valid():
        login(request, user=form.get_user())

        return redirect("/")
    
    return render(request, "accounts/login.html", context={"form": form})

def logout_view(request: HttpRequest):
    logout(request)
    return redirect("/")
    