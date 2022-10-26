from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms

from .models import RoleChoices


class MyAuthForm(AuthenticationForm):
    ordered_fields_name = ('role', 'username', 'password')

    role = forms.ChoiceField(
        choices=RoleChoices.choices,
        label="Login sebagai"
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