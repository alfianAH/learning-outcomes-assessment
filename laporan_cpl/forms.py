from django import forms
from django.forms import (
    formset_factory,
    BaseFormSet
)
from learning_outcomes_assessment.forms.formset import CanDeleteBaseFormSet
from learning_outcomes_assessment.widgets import MySelectInput
from kurikulum.models import Kurikulum
from semester.models import TahunAjaranProdi


class KurikulumChoiceForm(forms.Form):
    kurikulum = forms.ModelChoiceField(
        widget=MySelectInput(),
        required=False,
        queryset=None,
    )

    def __init__(self, prodi, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['kurikulum'].queryset = Kurikulum.objects.filter(
            prodi_jenjang__program_studi=prodi
        )


class TahunAjaranSemesterChoiceForm(forms.Form):
    tahun_ajaran = forms.ChoiceField(
        widget=MySelectInput(
            attrs={
                'class': 'tahun-ajaran'
            }
        ),
        required=False,
        choices=(('', '---------'),)
    )
    semester = forms.ChoiceField(
        widget=MySelectInput(
            attrs={
                'class': 'semester'
            }
        ),
        required=False,
        choices=(('', '---------'),)
    )


class TahunAjaranSemesterFormsetClass(CanDeleteBaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if len(args) > 1: return
        data = args[0]
        self.kurikulum_id = data.get('kurikulum')

        tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
            semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=self.kurikulum_id
        ).distinct()
        tahun_ajaran_choices = [(tahun_ajaran_prodi.pk, str(tahun_ajaran_prodi.tahun_ajaran)) for tahun_ajaran_prodi in tahun_ajaran_prodi_qs]
        
        self.initial_choices = {}
        for form in self.forms:
            form.fields['tahun_ajaran'].choices += tahun_ajaran_choices

            self.initial_choices[form.prefix] = {
                'tahun_ajaran': form.fields['tahun_ajaran'].choices,
                'semester': form.fields['semester'].choices,
            }
        
        print(self.initial_choices)
    
    def clean(self):
        super().clean()

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue

            print('clean:', form.cleaned_data)


TahunAjaranSemesterFormset = formset_factory(
    TahunAjaranSemesterChoiceForm,
    formset=TahunAjaranSemesterFormsetClass,
    extra=0,
    can_delete=True,
    validate_max=False,
    min_num=1,
)
