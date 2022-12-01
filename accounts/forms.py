from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from .enums import RoleChoices
from .widgets import LoginTextInput, LoginPasswordInput


class MahasiswaAuthForm(AuthenticationForm):
    username = forms.CharField(
        widget=LoginTextInput(
            attrs={
                "placeholder": "Username"
            }
        )
    )

    password = forms.CharField(
        widget=LoginPasswordInput(
            attrs={
                "placeholder": "Password"
            }
        )
    )

    def __init__(self, request, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, user=username, password=password, role=RoleChoices.MAHASISWA)
            
            if self.user_cache is None:
                self.add_error("username", "Username anda salah")
                self.add_error("password", "Password anda salah")
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
