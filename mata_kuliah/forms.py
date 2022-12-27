from django import forms
from django.conf import settings
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA,
    UpdateChoiceList,
)
from .utils import get_update_mk_kurikulum_choices


class MataKuliahKurikulumCreateForm(forms.Form):
    mk_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='mata-kuliah/partials/list-custom-field-mk.html',
            table_custom_field_template='mata-kuliah/partials/table-custom-field-mk.html',
            table_custom_field_header_template='mata-kuliah/partials/table-custom-field-header-mk.html',
        ),
        label = 'Tambahkan Mata Kuliah Kurikulum dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.',
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


class MataKuliahKurikulumBulkUpdateForm(forms.Form):
    update_data_mk_kurikulum = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            list_custom_field_template='mata-kuliah/partials/list-custom-field-mk.html',
        ),
        label = 'Update Data Mata Kuliah Kurikulum',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        kurikulum_id = kwargs.pop('kurikulum_id')
        prodi_id = kwargs.pop('prodi_id')
        super().__init__(*args, **kwargs)

        update_mk_kurikulum_choices = get_update_mk_kurikulum_choices(kurikulum_id, prodi_id)

        self.fields['update_data_mk_kurikulum'].choices = update_mk_kurikulum_choices


class MataKuliahSemesterCreateForm(forms.Form):
    mk_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='mata-kuliah/partials/list-custom-field-mk-semester.html',
            table_custom_field_template='mata-kuliah/partials/table-custom-field-mk-semester.html',
            table_custom_field_header_template='mata-kuliah/partials/table-custom-field-header-mk-semester.html',
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
