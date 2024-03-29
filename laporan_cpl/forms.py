from django import forms
from django.forms import (
    formset_factory,
)
from learning_outcomes_assessment.forms.formset import CanDeleteBaseFormSet
from learning_outcomes_assessment.widgets import (
    MySelectInput,
    ChoiceListInteractiveModelA
)
from kurikulum.models import Kurikulum
from mata_kuliah_semester.models import PesertaMataKuliah
from semester.models import (
    TahunAjaranProdi,
    SemesterProdi
)


class KurikulumChoiceForm(forms.Form):
    kurikulum = forms.ModelChoiceField(
        widget=MySelectInput(),
        required=False,
        queryset=None,
        help_text='Pilih kurikulum untuk menampilkan tahun ajaran yang diinginkan.',
    )

    def __init__(self, prodi, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields['kurikulum'].queryset = Kurikulum.objects.filter(
                prodi_jenjang__program_studi=prodi
            )
        else:
            self.fields['kurikulum'].queryset = Kurikulum.objects.filter(
                prodi_jenjang__program_studi=prodi,
                matakuliahkurikulum__matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa=user
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        kurikulum = cleaned_data.get('kurikulum')
        
        if kurikulum is None:
            self.add_error('kurikulum', 'Harus memilih kurikulum sebelum melakukan filter.')
        return cleaned_data


class MataKuliahSemesterExcludeForm(forms.Form):
    mk_semester = forms.MultipleChoiceField(
        widget=ChoiceListInteractiveModelA(
            list_custom_field_template='laporan-cpl/partials/mahasiswa/filter-mk/list-custom-field-filter-mk.html',
            table_custom_field_template='laporan-cpl/partials/mahasiswa/filter-mk/table-custom-field-filter-mk.html',
            table_custom_field_header_template='laporan-cpl/partials/mahasiswa/filter-mk/table-custom-field-header-filter-mk.html',
            custom_option_template_name='laporan-cpl/partials/mahasiswa/filter-mk/custom-option-template-name-filter-mk.html'
        ),
        label='Pilih mata kuliah semester yang ingin dikecualikan',
        required=False,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mk_semester'].choices = [
            (peserta.id_neosia, peserta) for peserta in PesertaMataKuliah.objects.filter(mahasiswa=user)
        ]

    def clean(self):
        cleaned_data = super().clean()
        
        # Clean MK Semester IDs
        mk_semester = cleaned_data.get('mk_semester')
        mk_semester = [*set(mk_semester)]
        
        cleaned_data['mk_semester'] = mk_semester

        return cleaned_data


class TahunAjaranSemesterChoiceForm(forms.Form):
    tahun_ajaran = forms.ChoiceField(
        widget=MySelectInput(
            attrs={
                'class': 'tahun-ajaran min-w-36'
            }
        ),
        required=False,
        choices=[('', '---------'),],
        help_text='Pilih tahun ajaran untuk menampilkan semester yang diinginkan.',
    )
    semester = forms.ChoiceField(
        widget=MySelectInput(
            attrs={
                'class': 'semester min-w-72'
            }
        ),
        required=False,
        choices=[('', '---------'),],
        help_text='Opsional. Anda harus memilih antara memilih "tahun ajaran" saja atau memilih "tahun ajaran dan semester".',
    )


class TahunAjaranSemesterFormsetClass(CanDeleteBaseFormSet):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.forms_to_delete = []
        
        data = kwargs.get('data')
        if data is None: return
        
        self.kurikulum_id = data.get('kurikulum')
        if self.kurikulum_id is None: return
        # Return if kurikulum id is blank
        if not self.kurikulum_id.strip(): return

        if user is None:
            tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
                semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=self.kurikulum_id
            ).distinct()
        else:
            tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
                semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=self.kurikulum_id,
                semesterprodi__matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa=user
            ).distinct()
        
        self.tahun_ajaran_choices = [(tahun_ajaran_prodi.pk, str(tahun_ajaran_prodi.tahun_ajaran)) for tahun_ajaran_prodi in tahun_ajaran_prodi_qs]
        
        # Add choices to form
        for form in self.forms:
            form.fields['tahun_ajaran'].choices += self.tahun_ajaran_choices

            # Get tahun ajaran
            tahun_ajaran_id: str = data.get('{}-tahun_ajaran'.format(form.prefix), '')
            # If tahun_ajaran id is empty, skip
            if not tahun_ajaran_id.strip(): continue
            
            # Get semester
            if user is None:
                semester_prodi_qs = SemesterProdi.objects.filter(
                    tahun_ajaran_prodi=tahun_ajaran_id
                )
            else:
                semester_prodi_qs = SemesterProdi.objects.filter(
                    tahun_ajaran_prodi=tahun_ajaran_id,
                    matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa=user
                ).distinct()
            self.semester_choices = [(semester_prodi.pk, semester_prodi.semester.nama) for semester_prodi in semester_prodi_qs]

            form.fields['semester'].choices += self.semester_choices
    
    @property
    def empty_form(self):
        empty_form = super().empty_form

        # If it is init, return normal empty form
        # Init doesn't have data so, it doesn't have this attrs
        if not hasattr(self, 'tahun_ajaran_choices') or not hasattr(self, 'semester_choices'): return empty_form

        # Add choices to empty form
        empty_form.fields['tahun_ajaran'].choices += self.tahun_ajaran_choices
        empty_form.fields['semester'].choices += self.semester_choices

        return empty_form
    
    def non_form_errors(self):
        errors = super().non_form_errors()
        
        if self.is_bound:
            # Get valid forms that is not deleted
            forms_valid = [
                form for form in self.forms
                if not (self.can_delete and self._should_delete_form(form))
            ]
        
        return errors

    def clean(self):
        super().clean()

        is_semester_included = False
        forms_to_delete = []
        for i, form in enumerate(self.forms):
            # If form is deleted, skip
            if self._should_delete_form(form):
                forms_to_delete.append(form)
                continue
            
            cleaned_data = form.cleaned_data

            tahun_ajaran: str = cleaned_data.get('tahun_ajaran', '')
            if not tahun_ajaran.strip():
                form.add_error('tahun_ajaran', 'Tahun ajaran harus dipilih atau anda bisa menghapus filter ini.')
            
            semester: str = cleaned_data.get('semester', '')

            # If semester is not empty, semester is included
            if i == 0 and semester.strip():
                is_semester_included = True

            # If semester is included and semester is empty, ...
            if is_semester_included and not semester.strip():
                form.add_error('semester', 'Filter form hanya menerima memilih "tahun ajaran" saja atau memilih "tahun ajaran dan semester". Form pertama: memilih "tahun ajaran dan semester".')
            # If semester is not included and semester is not empty, ...
            elif not is_semester_included and semester.strip():
                form.add_error('semester', 'Filter form hanya menerima memilih "tahun ajaran" saja atau memilih "tahun ajaran dan semester". Form pertama: memilih "tahun ajaran" saja.')

        for form in forms_to_delete:
            self.forms.remove(form)


TahunAjaranSemesterFormset = formset_factory(
    TahunAjaranSemesterChoiceForm,
    formset=TahunAjaranSemesterFormsetClass,
    extra=0,
    can_delete=True,
)
