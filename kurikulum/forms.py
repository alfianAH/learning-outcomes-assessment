from django import forms
from django.forms import CheckboxSelectMultiple
from .utils import get_kurikulum_by_prodi


class KurikulumReadAllSyncForm(forms.Form):
    kurikulum_from_neosia = None
    update_kurikulum_from_neosia = None
    semester_from_neosia = None
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        kurikulum_datas = get_kurikulum_by_prodi(self.user.prodi.id_neosia)
        kurikulum_choices = []

        for kurikulum_data in kurikulum_datas:
            kurikulum_choice = {
                'id_neosia': kurikulum_data['id'],
                'prodi': kurikulum_data['id_prodi'],
                'nama': kurikulum_data['nama'],
                'tahun_mulai': kurikulum_data['tahun'],
                'is_active': kurikulum_data['is_current'] == 1,
            }

            kurikulum_choices.append(kurikulum_choice)
        
        print(kurikulum_choices)
        self.kurikulum_from_neosia = forms.MultipleChoiceField(
            choices=kurikulum_choices,
            widget=forms.CheckboxSelectMultiple,
        )
