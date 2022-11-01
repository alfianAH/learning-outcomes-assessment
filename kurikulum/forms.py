from django import forms
from widgets.widgets import ChoiceListInteractive
from .utils import get_kurikulum_by_prodi


class KurikulumReadAllSyncForm(forms.Form):
    kurikulum_from_neosia = None
    update_kurikulum_from_neosia = None
    semester_from_neosia = None
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        self.label_suffix = "" 
        
        kurikulum_choices = get_kurikulum_by_prodi(self.user.prodi.id_neosia)
        
        print(kurikulum_choices)
        choice_list_widget = ChoiceListInteractive(
            badge_template='kurikulum/partials/badge-list-kurikulum.html',
            custom_field_template='kurikulum/partials/custom-field-list-kurikulum.html',
        )
        self.fields['kurikulum_from_neosia'] = forms.MultipleChoiceField(
            choices=kurikulum_choices,
            widget=choice_list_widget,
            label='Tambahkan Kurikukulum dari Neosia',
            help_text='Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
        )
