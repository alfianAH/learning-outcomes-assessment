from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from learning_outcomes_assessment import settings
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA,
    MyNumberInput,
)
from .enums import RoleChoices
from .widgets import LoginTextInput, LoginPasswordInput
from .utils import get_all_prodi_choices


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

class ProgramStudiJenjangForm(forms.Form):
    prodi_jenjang_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='accounts/prodi/partials/list-custom-field-prodi-jenjang.html',
            table_custom_field_template='accounts/prodi/partials/table-custom-field-prodi-jenjang.html',
            table_custom_field_header_template='accounts/prodi/partials/table-custom-field-header-prodi-jenjang.html',
        ),
        label = 'Tambahkan Program Studi dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prodi_jenjang_from_neosia'].choices = get_all_prodi_choices()

    def clean(self):
        cleaned_data = super().clean()

        # Clean prodi jenjang IDs
        prodi_jenjang_from_neosia = cleaned_data.get('prodi_jenjang_from_neosia')
        prodi_jenjang_from_neosia = [*set(prodi_jenjang_from_neosia)]
        
        cleaned_data['prodi_jenjang_from_neosia'] = prodi_jenjang_from_neosia
        is_prodi_jenjang_valid = len(prodi_jenjang_from_neosia) > 0
        
        if not is_prodi_jenjang_valid:
            self.add_error('prodi_jenjang_from_neosia', 'Pilih minimal 1 (satu) jenjang program studi')

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data
