from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms

from .models import RoleChoices
from .widgets import LoginTextInput, LoginPasswordInput, LoginSelect


class MyAuthForm(AuthenticationForm):
    ordered_fields_name = ('role', 'username', 'password')

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

    role = forms.ChoiceField(
        choices=RoleChoices.choices,
        widget=LoginSelect()
    )

    def __init__(self, request, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)
        self.rearrange_fields_order()

    def clean(self):
        role = self.cleaned_data.get('role')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password, role=role)
            
            if self.user_cache is None:
                self.add_error("username", "Username anda salah")
                self.add_error("password", "Password anda salah")
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def rearrange_fields_order(self):
        """Rearrage fields order for login form
        Order: role, username, password
        """
        new_ordered_fields = {}

        for field_name in self.ordered_fields_name:
            field = self.fields[field_name]
            if field:
                new_ordered_fields[field_name] = field
        
        self.fields = new_ordered_fields