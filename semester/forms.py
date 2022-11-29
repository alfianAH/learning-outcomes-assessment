from django import forms
from django.conf import settings

from .utils import (
    get_update_semester_choices,
)
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA, 
    UpdateChoiceList,
)


class SemesterFromNeosia(forms.Form):
    semester_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            badge_template='semester/partials/badge-list-semester.html',
            list_custom_field_template='semester/partials/list-custom-field-semester.html',
            table_custom_field_template='semester/partials/table-custom-field-semester.html',
            table_custom_field_header_template='semester/partials/table-custom-field-header-semester.html',
        ),
        label = 'Tambahkan Semester dari Neosia',
        help_text = 'Data di bawah ini merupakan data semester, dari Neosia, berdasarkan kurikulum yang dipilih pada langkah 1. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    def clean(self):
        cleaned_data = super().clean()
        if len(self.fields['semester_from_neosia'].choices) == 0: return cleaned_data

        # Clean kurikulum IDs
        semester_from_neosia = cleaned_data.get('semester_from_neosia')
        new_id_semester_from_neosia = []
        
        for id in semester_from_neosia:
            if id in new_id_semester_from_neosia: continue
            new_id_semester_from_neosia.append(id)
        
        cleaned_data['semester_from_neosia'] = new_id_semester_from_neosia

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class BulkUpdateSemester(forms.Form):
    update_data_semester = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            badge_template='semester/partials/badge-list-semester.html',
            list_custom_field_template='semester/partials/list-custom-field-semester.html',
        ),
        label = 'Update Data Semester',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        update_semester_choices = get_update_semester_choices(self.user.prodi.id_neosia)

        self.fields['update_data_semester'].choices = update_semester_choices
