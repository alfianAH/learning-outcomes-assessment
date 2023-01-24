from django import forms
from django.conf import settings
from .utils import (
    get_update_kelas_mk_semester_choices,
    get_update_peserta_mk_semester_choices,
)
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA,
    UpdateChoiceList,
)


class MataKuliahSemesterCreateForm(forms.Form):
    mk_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='mata-kuliah-semester/partials/list-custom-field-mk-semester.html',
            table_custom_field_template='mata-kuliah-semester/partials/table-custom-field-mk-semester.html',
            table_custom_field_header_template='mata-kuliah-semester/partials/table-custom-field-header-mk-semester.html',
        ),
        label = 'Tambahkan Mata Kuliah Semester dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.<br>Jika mata kuliah semester yang anda cari tidak ada, ada kemungkinan data sudah disinkronisasi atau mata kuliah pada kurikulum belum ditambahkan.<br><p class="text-danger">Disarankan menambahkan mata kuliah pada 1 kurikulum sebelumnya untuk menampilkan MK Semester pada kurikulum sebelumnya, untuk mencegah mata kuliah yang dicari tidak ada yang disebabkan pergantian kurikulum.</p>',
        required = False,
    )

    def clean(self):
        cleaned_data = super().clean()
        if len(self.fields['mk_from_neosia'].choices) == 0: return cleaned_data

        # Clean kurikulum IDs
        mk_from_neosia = cleaned_data.get('mk_from_neosia')
        mk_from_neosia = [*set(mk_from_neosia)]
        
        cleaned_data['mk_from_neosia'] = mk_from_neosia

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class KelasMataKuliahSemesterUpdateForm(forms.Form):
    update_data_kelas_mk_semester = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            list_custom_field_template='mata-kuliah-semester/partials/list-update-custom-field-mk-semester.html',
        ),
        label = 'Update Data Kelas Mata Kuliah Semester',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        mk_semester = kwargs.pop('mk_semester')
        super().__init__(*args, **kwargs)

        update_data_kelas_mk_semester_choices = get_update_kelas_mk_semester_choices(mk_semester)
        self.fields['update_data_kelas_mk_semester'].choices = update_data_kelas_mk_semester_choices


class PesertaMataKuliahSemesterCreateForm(forms.Form):
    peserta_mk_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='mata-kuliah-semester/partials/peserta/list-custom-field-peserta-mk-semester.html',
            table_custom_field_template='mata-kuliah-semester/partials/peserta/table-custom-field-peserta-mk-semester.html',
            table_custom_field_header_template='mata-kuliah-semester/partials/peserta/table-custom-field-header-peserta-mk-semester-form.html',
        ),
        label = 'Tambahkan Peserta Mata Kuliah Semester dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
        required = False,
    )

    def clean(self):
        cleaned_data = super().clean()
        if len(self.fields['peserta_mk_from_neosia'].choices) == 0: return cleaned_data

        # Clean kurikulum IDs
        peserta_mk_from_neosia = cleaned_data.get('peserta_mk_from_neosia')
        peserta_mk_from_neosia = [*set(peserta_mk_from_neosia)]
        
        cleaned_data['peserta_mk_from_neosia'] = peserta_mk_from_neosia

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class PesertaMataKuliahSemesterUpdateForm(forms.Form):
    update_peserta = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            list_custom_field_template='mata-kuliah-semester/partials/peserta/list-custom-field-peserta-mk-semester.html',
            list_item_name='mata-kuliah-semester/partials/peserta/list-item-name-peserta-mk-semester.html'
        ),
        label = 'Update Data Peserta Mata Kuliah Semester',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )
