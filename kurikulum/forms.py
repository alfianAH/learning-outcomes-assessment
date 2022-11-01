from django import forms
from django.conf import settings
from widgets.widgets import ChoiceListInteractive
from .utils import get_kurikulum_by_prodi


class KurikulumReadAllSyncForm(forms.Form):
    kurikulum_from_neosia = forms.MultipleChoiceField(
        # widget=forms.CheckboxSelectMultiple,
        widget=ChoiceListInteractive(
            badge_template='kurikulum/partials/badge-list-kurikulum.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-kurikulum.html',
            table_custom_field_template='kurikulum/partials/table-custom-field-kurikulum.html',
        ),
        label = 'Tambahkan Kurikulum dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        
        kurikulum_choices = get_kurikulum_by_prodi(self.user.prodi.id_neosia)
        print(self.fields)
        self.fields['kurikulum_from_neosia'].choices = kurikulum_choices
    
    def clean(self):
        cleaned_data = super().clean()
        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        return cleaned_data
