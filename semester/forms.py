from django import forms
from django.conf import settings

from accounts.models import ProgramStudi

from .utils import (
    get_semester_prodi_choices,
    get_update_semester_prodi_choices,
)
from mata_kuliah_semester.utils import(
    get_kelas_mk_semester,
)
from mata_kuliah_semester.models import MataKuliahSemester
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA, 
    UpdateChoiceList,
)


class SemesterProdiCreateForm(forms.Form):
    semester_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            badge_template='semester/partials/badge-list-semester-prodi.html',
            list_custom_field_template='semester/partials/list-custom-field-semester-prodi.html',
            table_custom_field_template='semester/partials/table-custom-field-semester-prodi.html',
            table_custom_field_header_template='semester/partials/table-custom-field-header-semester-prodi.html',
        ),
        label = 'Tambahkan Semester dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.<br>Note: Data semester yang tidak bisa dicentang berarti semester tidak memiliki data mata kuliah di Neosia atau mata kuliah semester sudah disinkronisasi semuanya.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        prodi_jenjang_id = kwargs.pop('prodi_jenjang_id')
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

        semester_prodi_choices = get_semester_prodi_choices(prodi_jenjang_id)

        for semester_prodi_id, _ in semester_prodi_choices:
            kelas_mk_semester = get_kelas_mk_semester(semester_prodi_id)

            if len(kelas_mk_semester) == 0: 
                # Set input with semester that has no MK Semester to false
                self.fields.get('semester_from_neosia').widget.condition_dict.update({
                    semester_prodi_id: False
                })

        self.fields['semester_from_neosia'].choices = semester_prodi_choices

    def clean(self):
        cleaned_data = super().clean()
        if len(self.fields['semester_from_neosia'].choices) == 0: return cleaned_data

        # Clean kurikulum IDs
        semester_from_neosia = cleaned_data.get('semester_from_neosia')
        semester_from_neosia = [*set(semester_from_neosia)]
        cleaned_data['semester_from_neosia'] = semester_from_neosia

        is_semester_valid = len(semester_from_neosia) > 0

        if not is_semester_valid:
            self.add_error('semester_from_neosia', 'Pilih minimal 1 (satu) semester')

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class SemesterProdiBulkUpdateForm(forms.Form):
    update_data_semester = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            badge_template='semester/partials/badge-list-semester-prodi.html',
            list_custom_field_template='semester/partials/list-custom-field-semester-prodi.html',
            list_item_name='semester/partials/list-item-name-semester-prodi.html',
        ),
        label = 'Update Data Semester',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        prodi_obj: ProgramStudi = user.prodi
        update_semester_choices = get_update_semester_prodi_choices(prodi_obj)

        self.fields['update_data_semester'].choices = update_semester_choices
