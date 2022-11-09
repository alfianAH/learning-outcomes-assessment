from django import forms
from django.conf import settings
from widgets.widgets import ChoiceListInteractive
from .utils import (
    get_kurikulum_by_prodi,
    get_all_semester,
)


class KurikulumFromNeosia(forms.Form):
    kurikulum_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractive(
            badge_template='kurikulum/partials/badge-list-kurikulum.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-kurikulum.html',
            table_custom_field_template='kurikulum/partials/table-custom-field-kurikulum.html',
            table_custom_field_header_template='kurikulum/partials/table-custom-field-header-kurikulum.html',
        ),
        label = 'Tambahkan Kurikulum dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        kurikulum_choices = get_kurikulum_by_prodi(self.user.prodi.id_neosia)
        self.fields['kurikulum_from_neosia'].choices = kurikulum_choices

    def clean(self):
        cleaned_data = super().clean()

        # Clean kurikulum IDs
        kurikulum_from_neosia = cleaned_data.get('kurikulum_from_neosia')
        new_id_kurikulum_from_neosia = []
        
        for id in kurikulum_from_neosia:
            if id in new_id_kurikulum_from_neosia: continue
            new_id_kurikulum_from_neosia.append(id)
        
        cleaned_data['kurikulum_from_neosia'] = new_id_kurikulum_from_neosia

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class SemesterFromNeosia(forms.Form):
    semester_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractive(
            badge_template='kurikulum/partials/badge-list-semester.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-semester.html',
            table_custom_field_template='kurikulum/partials/table-custom-field-semester.html',
            table_custom_field_header_template='kurikulum/partials/table-custom-field-header-semester.html',
        ),
        label = 'Tambahkan Semester dari Neosia',
        help_text = 'Data di bawah ini merupakan data semester, dari Neosia, berdasarkan kurikulum yang dipilih pada langkah 1. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        
        semester_choices = get_all_semester()
        self.fields['semester_from_neosia'].choices = semester_choices


class KurikulumReadAllSyncForm(forms.Form):
    kurikulum_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractive(
            badge_template='kurikulum/partials/badge-list-kurikulum.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-kurikulum.html',
            table_custom_field_template='kurikulum/partials/table-custom-field-kurikulum.html',
            table_custom_field_header_template='kurikulum/partials/table-custom-field-header-kurikulum.html',
        ),
        label = 'Tambahkan Kurikulum dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )
    semester_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractive(
            badge_template='kurikulum/partials/badge-list-semester.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-semester.html',
            table_custom_field_template='kurikulum/partials/table-custom-field-semester.html',
            table_custom_field_header_template='kurikulum/partials/table-custom-field-header-semester.html',
        ),
        label = 'Tambahkan Semester dari Neosia',
        help_text = 'Data di bawah ini merupakan data semester, dari Neosia, berdasarkan kurikulum yang dipilih pada langkah 1. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        
        kurikulum_choices = get_kurikulum_by_prodi(self.user.prodi.id_neosia)
        semester_choices = get_all_semester()
        
        self.fields['kurikulum_from_neosia'].choices = kurikulum_choices
        self.fields['semester_from_neosia'].choices = semester_choices
    
    def clean(self):
        cleaned_data = super().clean()

        # Clean kurikulum IDs
        kurikulum_from_neosia = cleaned_data.get('kurikulum_from_neosia')
        new_id_kurikulum_from_neosia = []
        
        for id in kurikulum_from_neosia:
            if id in new_id_kurikulum_from_neosia: continue
            new_id_kurikulum_from_neosia.append(id)
        
        cleaned_data['kurikulum_from_neosia'] = new_id_kurikulum_from_neosia

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data
