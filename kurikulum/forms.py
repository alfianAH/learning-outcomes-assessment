from django import forms
from django.conf import settings
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA,
    UpdateChoiceList,
)
from mata_kuliah_kurikulum.models import MataKuliahKurikulum
from mata_kuliah_kurikulum.utils import(
    get_mk_kurikulum,
)
from .utils import (
    get_kurikulum_by_prodi_jenjang_choices,
    get_update_kurikulum_choices,
)


class KurikulumCreateForm(forms.Form):
    kurikulum_from_neosia = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            badge_template='kurikulum/partials/badge-list-kurikulum.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-kurikulum.html',
            table_custom_field_template='kurikulum/partials/table-custom-field-kurikulum.html',
            table_custom_field_header_template='kurikulum/partials/table-custom-field-header-kurikulum.html',
        ),
        label = 'Tambahkan Kurikulum dari Neosia',
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.<br>Note: Data kurikulum yang tidak bisa dicentang berarti kurikulum tidak memiliki data mata kuliah di Neosia atau mata kuliah sudah disinkronisasi semuanya.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        prodi_jenjang_id = kwargs.pop('prodi_jenjang_id')
        super().__init__(*args, **kwargs)
        
        kurikulum_choices = get_kurikulum_by_prodi_jenjang_choices(prodi_jenjang_id)
        
        for kurikulum_id, _ in kurikulum_choices:
            mk_kurikulum = get_mk_kurikulum(kurikulum_id, prodi_jenjang_id)

            if len(mk_kurikulum) > 0: 
                # Check in database
                is_all_mk_sync = True
                for mk_data in mk_kurikulum:
                    mk_id = mk_data['id_neosia']
                    mk_in_db = MataKuliahKurikulum.objects.filter(id_neosia=int(mk_id), kurikulum=kurikulum_id)
                    if mk_in_db.exists(): continue
                    # Break and set to False if kurikulum has one or more MK Kurikulum to sync
                    is_all_mk_sync = False
                    break
                
                # If all MK Kurikulum is already synchronized, remove kurikulum choices
                if is_all_mk_sync:
                    # Set input with kurikulum that has no semester to false
                    self.fields.get('kurikulum_from_neosia').widget.condition_dict.update({
                        kurikulum_id: False
                    })
                continue
            
            # Set input with kurikulum that has no MK Kurikulum to false
            self.fields.get('kurikulum_from_neosia').widget.condition_dict.update({
                kurikulum_id: False
            })
        
        self.fields['kurikulum_from_neosia'].choices = kurikulum_choices

    def clean(self):
        cleaned_data = super().clean()

        # Clean kurikulum IDs
        kurikulum_from_neosia = cleaned_data.get('kurikulum_from_neosia')
        kurikulum_from_neosia = [*set(kurikulum_from_neosia)]
        
        cleaned_data['kurikulum_from_neosia'] = kurikulum_from_neosia
        is_kurikulum_valid = len(kurikulum_from_neosia) > 0
        
        if not is_kurikulum_valid:
            self.add_error('kurikulum_from_neosia', 'Pilih minimal 1 (satu) kurikulum')

        if settings.DEBUG: print("Clean data: {}".format(cleaned_data))
        
        return cleaned_data


class KurikulumBulkUpdateForm(forms.Form):
    update_data_kurikulum = forms.MultipleChoiceField(
        widget=UpdateChoiceList(
            badge_template='kurikulum/partials/badge-list-kurikulum.html',
            list_custom_field_template='kurikulum/partials/list-custom-field-kurikulum.html',
        ),
        label = 'Update Data Kurikulum',
        help_text = 'Data yang berwarna hijau merupakan data terbaru dari Neosia.<br>Data yang berwarna merah merupakan data lama pada sistem ini.<br>Beri centang pada item yang ingin anda update.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        update_kurikulum_choices = get_update_kurikulum_choices(self.user.prodi.id_neosia)

        self.fields['update_data_kurikulum'].choices = update_kurikulum_choices
