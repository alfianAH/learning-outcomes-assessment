from django import forms
from django.conf import settings
from semester.models import SemesterKurikulum
from learning_outcomes_assessment.widgets import (
    ChoiceListInteractiveModelA,
    UpdateChoiceList,
)
from semester.utils import (
    get_semester_by_kurikulum,
)
from .utils import (
    get_kurikulum_by_prodi_choices,
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
        help_text = 'Data di bawah ini merupakan data baru dari Neosia dan belum ditemukan dalam database. Beri centang pada item yang ingin anda tambahkan.<br>Note: Data kurikulum yang tidak bisa dicentang berarti kurikulum tidak memiliki data semester di Neosia.',
        required = False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        kurikulum_choices = get_kurikulum_by_prodi_choices(self.user.prodi.id_neosia)

        for i, (kurikulum_id, _) in enumerate(kurikulum_choices):
            semester_by_kurikulum = get_semester_by_kurikulum(kurikulum_id)

            if len(semester_by_kurikulum) > 0: 
                # Check in database
                is_all_semester_sync = True
                for semester_data in semester_by_kurikulum:
                    semester_id = semester_data['id_neosia']
                    semester_in_db = SemesterKurikulum.objects.filter(semester=int(semester_id), kurikulum=kurikulum_id)
                    if semester_in_db.exists(): continue
                    # Break and set to False if kurikulum has one or more semester to sync
                    is_all_semester_sync = False
                    break
                
                # If all semester is already synchronized, remove kurikulum choices
                if is_all_semester_sync: 
                    kurikulum_choices.pop(i)
                continue
            
            # Set input with kurikulum that has no semester to false
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
