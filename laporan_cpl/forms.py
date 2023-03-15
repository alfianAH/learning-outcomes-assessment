from django import forms
from django.forms import (
    formset_factory,
    BaseFormSet
)
from learning_outcomes_assessment.forms.formset import CanDeleteBaseFormSet
from learning_outcomes_assessment.widgets import MySelectInput
from kurikulum.models import Kurikulum
from semester.models import (
    TahunAjaranProdi,
    SemesterProdi
)


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

    def clean(self):
        cleaned_data = super().clean()
        kurikulum = cleaned_data.get('kurikulum')
        
        if kurikulum is None:
            self.add_error('kurikulum', 'Harus memilih kurikulum sebelum melakukan filter.')
        return cleaned_data


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
        if data is None: return
        
        self.kurikulum_id = data.get('kurikulum')
        # Return if kurikulum id is blank
        if not self.kurikulum_id.strip(): return
        
        print(args, kwargs)

        tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
            semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=self.kurikulum_id
        ).distinct()
        semester_prodi_qs = SemesterProdi.objects.filter(
            tahun_ajaran_prodi__in=tahun_ajaran_prodi_qs
        )
        tahun_ajaran_choices = [(tahun_ajaran_prodi.pk, str(tahun_ajaran_prodi.tahun_ajaran)) for tahun_ajaran_prodi in tahun_ajaran_prodi_qs]
        semester_choices = [(semester_prodi.pk, semester_prodi.semester.nama) for semester_prodi in semester_prodi_qs]
        
        self.initial_choices = {}
        for form in self.forms:
            form.fields['tahun_ajaran'].choices += tahun_ajaran_choices
            form.fields['semester'].choices += semester_choices

            self.initial_choices[form.prefix] = {
                'tahun_ajaran': form.fields['tahun_ajaran'].choices,
                'semester': form.fields['semester'].choices,
            }
    
    def clean(self):
        super().clean()

        is_semester_included = False

        for i, form in enumerate(self.forms):
            if self._should_delete_form(form): continue
            cleaned_data = form.cleaned_data
            semester: str = cleaned_data.get('semester')
            
            # If semester is not empty, semester is included
            if i == 0 and semester.strip():
                is_semester_included = True

            # If semester is included and semester is empty, ...
            if is_semester_included and not semester.strip():
                form.add_error('semester', 'Filter form hanya menerima memilih "tahun ajaran" saja atau memilih "tahun ajaran dan semester". Form pertama: memilih "tahun ajaran dan semester".')
            elif not is_semester_included and semester.strip():
                form.add_error('semester', 'Filter form hanya menerima memilih "tahun ajaran" saja atau memilih "tahun ajaran dan semester". Form pertama: memilih "tahun ajaran" saja.')


TahunAjaranSemesterFormset = formset_factory(
    TahunAjaranSemesterChoiceForm,
    formset=TahunAjaranSemesterFormsetClass,
    extra=0,
    can_delete=True,
    validate_max=False,
    min_num=1,
)
