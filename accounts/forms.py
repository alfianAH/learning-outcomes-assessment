from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from learning_outcomes_assessment import settings
from learning_outcomes_assessment.widgets import (
    UpdateChoiceList,
    ChoiceListInteractiveModelA,
    MyNumberInput,
    MyRadioInput,
)
from .models import ProgramStudi, ProgramStudiJenjang
from .enums import RoleChoices
from .widgets import LoginTextInput, LoginPasswordInput
from .utils import (
    validate_mahasiswa,
    get_all_prodi_choices,
    get_prodi_jenjang_db_choices,
)


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

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            user_data = validate_mahasiswa(username, password)

            # Return None if user data is None
            if user_data is None: 
                if settings.DEBUG: print("User data is not valid: {}".format(username))
                self.add_error("username", "Username anda salah")
                self.add_error("password", "Password anda salah")
                raise self.get_invalid_login_error()

            self.user_cache = authenticate(self.request, user=user_data, role=RoleChoices.MAHASISWA)
            
            if self.user_cache is None:
                self.add_error("username", "Username anda salah")
                self.add_error("password", "Password anda salah")
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class ProgramStudiJenjangSelectForm(forms.Form):
    prodi_jenjang = forms.ChoiceField(
        widget=MyRadioInput(),
        label = 'Pilih Jenjang Program Studi',
        help_text = 'Berikut adalah list jenjang program studi. Pilih salah satu untuk memilih kurikulum, di step selanjutnya, yang sesuai dengan jenjang program studi masing-masing.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        prodi_obj: ProgramStudi = self.user.prodi
        self.fields['prodi_jenjang'].choices = get_prodi_jenjang_db_choices(prodi_obj)

    def clean(self):
        cleaned_data = super().clean()
        prodi_jenjang_id = cleaned_data['prodi_jenjang']

        if prodi_jenjang_id is None or prodi_jenjang_id == '':
            self.add_error('prodi_jenjang', 'Harus memilih jenjang program studi.')
            return cleaned_data

        try:
            prodi_jenjang_id = int(prodi_jenjang_id)
        except ValueError:
            if settings.DEBUG:
                print('Cannot convert prodi jenjang ID: {}'.format(prodi_jenjang_id))
            self.add_error('prodi_jenjang', 'Prodi jenjang yang dipilih: {}. Tidak bisa diconvert ke integer.'.format(prodi_jenjang_id))
        
        cleaned_data['prodi_jenjang'] = prodi_jenjang_id

        return cleaned_data


class ProgramStudiJenjangCreateForm(forms.Form):
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


class ProgramStudiJenjangUpdateForm(forms.Form):
    update_data_prodi_jenjang = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            list_custom_field_template='accounts/prodi/partials/list-custom-field-prodi-jenjang-wo-sks.html',
        ),
        label = 'Update Data Jenjang Program Studi',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )


class ProgramStudiJenjangModelForm(forms.ModelForm):
    class Meta:
        model = ProgramStudiJenjang
        fields = ['total_sks_lulus']
        labels = {
            'total_sks_lulus': 'Minimal SKS Kelulusan'
        }
        widgets = {
            'total_sks_lulus': MyNumberInput()
        }


class ProgramStudiJenjangInlineFormset(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form['total_sks_lulus'].label = 'Minimal SKS Kelulusan ({})'.format(form.instance.nama)


ProgramStudiJenjangModelFormset = inlineformset_factory(
    ProgramStudi,
    ProgramStudiJenjang,
    form=ProgramStudiJenjangModelForm,
    formset=ProgramStudiJenjangInlineFormset,
    can_delete=False,
    extra=0,
)
