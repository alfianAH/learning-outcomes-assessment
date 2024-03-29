from django import forms
from django.conf import settings
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA,
    UpdateChoiceList,
)


class MataKuliahKurikulumCreateForm(forms.Form):
    mk_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='mata-kuliah-kurikulum/partials/list-custom-field-mk-kurikulum.html',
            table_custom_field_template='mata-kuliah-kurikulum/partials/table-custom-field-mk-kurikulum.html',
            table_custom_field_header_template='mata-kuliah-kurikulum/partials/table-custom-field-header-mk-kurikulum.html',
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
        is_mk_kurikulum_valid = len(mk_from_neosia) > 0
        
        if not is_mk_kurikulum_valid:
            self.add_error('mk_from_neosia', 'Pilih minimal 1 (satu) mata kuliah kurikulum')
        
        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class MataKuliahKurikulumBulkUpdateForm(forms.Form):
    update_data_mk_kurikulum = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            list_custom_field_template='mata-kuliah-kurikulum/partials/list-custom-field-mk-kurikulum.html',
        ),
        label = 'Update Data Mata Kuliah Kurikulum',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )
