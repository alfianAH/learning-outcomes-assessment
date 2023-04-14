import math
from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.forms import inlineformset_factory, formset_factory
from learning_outcomes_assessment.forms.formset import CanDeleteInlineFormSet
from learning_outcomes_assessment.widgets import(
    MyCheckboxInput,
    MyNumberInput,
    MySelectInput,
    MyTextInput,
    MyTextareaInput,
    MyRadioInput,
)
from learning_outcomes_assessment.validators import validate_excel_file
from kurikulum.models import Kurikulum
from mata_kuliah_semester.models import (
    MataKuliahSemester,
    PesertaMataKuliah
)
from .models import (
    Clo,
    KomponenClo,
    NilaiKomponenCloPeserta,
)
from mata_kuliah_semester.utils import process_excel_file
from .utils import (
    get_pi_area_by_kurikulum_choices,
    get_pi_by_pi_area_choices,
    generate_nilai_clo,
)


class CloForm(forms.ModelForm):
    class Meta:
        model = Clo
        fields = ['nama', 'deskripsi']
        labels = {
            'nama': 'Nama CPMK'
        }
        widgets = {
            'nama': MyTextInput(attrs={
                'placeholder': 'Masukkan nama CPMK...',
            }),
            'deskripsi': MyTextareaInput(attrs={
                'placeholder': 'Masukkan deskripsi CPMK...',
                'cols': 30,
                'rows': 3,
            })
        }
        help_texts = {
            'nama': 'Nama CPMK. Contoh: <b>CPMK 1</b>',
        }


class CloDuplicateForm(forms.Form):
    semester = forms.ChoiceField(
        widget=MyRadioInput(),
        label='Duplikasi Capaian Pembelajaran Mata Kuliah',
    )

    def __init__(self, *args, **kwargs):
        mk_semester: MataKuliahSemester = kwargs.pop('mk_semester')
        choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)
        
        self.fields['semester'].help_text = 'Berikut adalah pilihan semester dari <b>{}</b>. Pilih salah satu semester untuk menduplikasi Capaian Pembelajaran Mata Kuliah dari semester tersebut ke <b>{}</b>'.format(mk_semester.mk_kurikulum.kurikulum.nama, mk_semester.semester.semester.nama)

        self.fields['semester'].choices = choices


class PerformanceIndicatorAreaForPiCloForm(forms.Form):
    pi_area = forms.ChoiceField(
        widget=MySelectInput(),
        label = 'Pilih ILO',
        required=True
    )

    def __init__(self, *args, **kwargs):
        kurikulum_obj: Kurikulum = kwargs.pop('kurikulum_obj')
        super().__init__(*args, **kwargs)
        pi_area_choices = get_pi_area_by_kurikulum_choices(kurikulum_obj)
        self.fields['pi_area'].choices = pi_area_choices
        self.fields['pi_area'].help_text = 'List ILO dari {}.'.format(kurikulum_obj.nama)

    def clean(self):
        cleaned_data = super().clean()

        # Get PI Area IDs
        pi_area = cleaned_data.get('pi_area', None)
        
        if pi_area is None:
            self.add_error('pi_area', 'Harus memilih salah satu ILO terlebih dahulu')
        
        return cleaned_data


class PiCloForm(forms.Form):
    performance_indicator = forms.MultipleChoiceField(
        widget=MyCheckboxInput(),
        label='Performance Indicators (PI)'
    )

    def __init__(self, *args, **kwargs):
        pi_area_id = kwargs.pop('pi_area_id')
        super().__init__(*args, **kwargs)
        self.fields['performance_indicator'].choices = get_pi_by_pi_area_choices(pi_area_id)


class KomponenCloForm(forms.ModelForm):
    class Meta:
        model = KomponenClo
        fields = ['teknik_penilaian', 'instrumen_penilaian', 'persentase']
        widgets = {
            'teknik_penilaian': MySelectInput(attrs={
                'class': 'teknik-penilaian-search',
                'placeholder': 'Masukkan teknik penilaian',
            }),
            'instrumen_penilaian': MyTextInput(attrs={
                'placeholder': 'Masukkan instrumen penilaian',
            }),
            'persentase': MyNumberInput(attrs={
                'placeholder': 'Persentase komponen',
                'min': 0,
                'max': 100,
                'step': 'any',
            })
        }
        help_texts = {
            'teknik_penilaian': 'Teknik penilaian terdiri dari <b>observasi</b>, <b>partisipasi</b>, <b>unjuk kerja</b>, <b>tes tertulis</b>, <b>tes lisan</b>, dan <b>angket</b>.',
            'instrumen_penilaian': 'Instrumen penilaian biasanya berupa <b>tugas</b>, <b>ujian mid</b>, <b>ujian final</b>, dll.',
            'persentase': 'Persentase tiap komponen CPMK (0-100).'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_permitted = False


class KomponenCloInlineFormset(CanDeleteInlineFormSet):
    def __init__(self, mk_semester, clo=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mk_semester: MataKuliahSemester = mk_semester
        self.current_clo: Clo = clo

    def clean(self) -> None:
        super().clean()

        # Sum all of percentages
        submitted_persentase = 0
        exist_persentase = 0

        for form in self.forms:
            is_field_deleted = form.cleaned_data.get('DELETE')
            persentase = form.cleaned_data.get('persentase', 0)
            komponen_id = form.cleaned_data.get('id')

            # Skip, if field is deleted
            if is_field_deleted: continue
            
            # If add new komponen, ...
            if komponen_id is None:
                # Add persentase to submitted
                submitted_persentase += persentase
            else:  # If komponen is already added, ...
                # Add persentase to exist
                exist_persentase += persentase
        
        if self.current_clo is None:
            total_persentase = self.mk_semester.get_total_persentase_clo() - exist_persentase + submitted_persentase
        else:
            old_clo_persentase = self.current_clo.get_total_persentase_komponen()
            new_clo_persentase = exist_persentase + submitted_persentase
            total_persentase = self.mk_semester.get_total_persentase_clo() - old_clo_persentase + new_clo_persentase
        
        print('Total: {}'.format(total_persentase))
        # Add error to field if total_persentase is more than 100
        if total_persentase > 100:
            for form in self.forms:
                form.add_error('persentase', 'Total persentase semua komponen penilaian saat ini: {}%. Total persentase tidak boleh melebihi 100%'.format(total_persentase))


KomponenCloFormset = inlineformset_factory(
    Clo,
    KomponenClo,
    form=KomponenCloForm,
    formset=KomponenCloInlineFormset,
    extra=1,
    can_delete=True,
)


class NilaiKomponenCloPesertaForm(forms.ModelForm):
    class Meta:
        model = NilaiKomponenCloPeserta
        fields = ['nilai', 'peserta', 'komponen_clo']
        widgets = {
            'nilai': MyNumberInput(attrs={
                'placeholder': 'Nilai (0-100)',
                'min': 0,
                'max': 100,
                'step': 'any',
                'class': 'w-full'
            }),
            'peserta': forms.HiddenInput(),
            'komponen_clo': forms.HiddenInput(),
        }


class NilaiKomponenCloPesertaFormsetClass(forms.BaseFormSet):
    def __init__(self, list_peserta_mk, list_komponen_clo, is_generate=False, is_import=False, import_result:dict=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.list_peserta_mk: list[PesertaMataKuliah] = list_peserta_mk
        self.list_komponen_clo: QuerySet[KomponenClo] = list_komponen_clo
        self.is_generate = is_generate

        # List persentase for each komponen CPMK
        list_persentase_komponen_clo = [komponen_clo.persentase for komponen_clo in self.list_komponen_clo]
        
        self.list_komponen_clo_len = self.list_komponen_clo.count()

        for i, peserta in enumerate(self.list_peserta_mk):
            can_generate = False

            for j, komponen_clo in enumerate(self.list_komponen_clo):
                # Use the right increment for form index
                form_index = i + i*(self.list_komponen_clo_len-1) + j
                
                self.forms[form_index].initial.update({
                    'peserta': peserta,
                    'komponen_clo': komponen_clo
                })

                # Set label
                self.forms[form_index].fields['nilai'].label = '{} - {} ({}%)'.format(komponen_clo.clo.nama, komponen_clo.instrumen_penilaian, komponen_clo.persentase)

                # Nilai Initial for import file
                if is_import and import_result is not None:
                    nim = peserta.mahasiswa.username

                    # Skip if there is no import result
                    if import_result.get(nim) is None: continue

                    self.forms[form_index].initial.update({
                        'nilai': import_result[nim][j]
                    })
                # Nilai Initial for manual input
                else:
                    nilai_peserta_qs = NilaiKomponenCloPeserta.objects.filter(
                        peserta=peserta,
                        komponen_clo=komponen_clo,
                    )

                    if nilai_peserta_qs.exists():
                        self.forms[form_index].initial.update({
                            'nilai': nilai_peserta_qs.first().nilai
                        })
                    else:
                        can_generate = True
            
            # Generate nilai
            if self.is_generate and can_generate:
                if settings.DEBUG: 
                    print('Generate: {}'.format(peserta.mahasiswa.nama))

                generated_nilai_peserta = generate_nilai_clo(list_persentase_komponen_clo, peserta.nilai_akhir)

                for j, komponen_clo in enumerate(self.list_komponen_clo):
                    # Use the right increment for form index
                    form_index = i + i*(self.list_komponen_clo_len-1) + j

                    self.forms[form_index].initial.update({
                        'nilai': generated_nilai_peserta[j],
                    })

    def total_form_count(self):
        return len(self.list_peserta_mk) * self.list_komponen_clo.count()
    
    def clean(self) -> None:
        for i, peserta in enumerate(self.list_peserta_mk):
            is_all_nilai_peserta_empty = []
            nilai_peserta = 0

            for j, komponen_clo in enumerate(self.list_komponen_clo):
                is_nilai_peserta_empty = False
                # Use the right increment for form index
                form_index = i + i*(self.list_komponen_clo_len-1) + j
                
                if self.forms[form_index].has_changed():
                    cleaned_data = self.forms[form_index].clean()
                    nilai_submit = cleaned_data.get('nilai', None)
                else:
                    init_data = self.forms[form_index].initial
                    nilai_submit = init_data.get('nilai', None)

                if nilai_submit is None:
                    is_nilai_peserta_empty = True
                    is_all_nilai_peserta_empty.append(is_nilai_peserta_empty)
                    continue
                
                nilai_peserta += komponen_clo.persentase/100 * nilai_submit
                is_all_nilai_peserta_empty.append(is_nilai_peserta_empty)
            
            # Use XNOR Logic to validate this
            # User can submit the form if all forms are filled or all forms are empty
            if all(is_all_nilai_peserta_empty) or not any(is_all_nilai_peserta_empty):
                # Continue if all forms are empty
                if all(is_all_nilai_peserta_empty):
                    continue
            else:
                self.forms[form_index].add_error(
                    'nilai', 
                    'Salah satu nilai tidak boleh kosong. Hanya diperbolehkan kosong semua atau terisi semua.'
                )
            
            if not math.isclose(nilai_peserta, peserta.nilai_akhir, rel_tol=1e-5, abs_tol=1):
                self.forms[form_index].add_error(
                    'nilai', 
                    'Nilai input tidak sesuai dengan nilai akhir. Nilai input: {:.2f}, Nilai akhir: {:.2f}'.format(nilai_peserta, peserta.nilai_akhir)
                )


NilaiKomponenCloPesertaFormset = formset_factory(
    NilaiKomponenCloPesertaForm,
    formset=NilaiKomponenCloPesertaFormsetClass,
    extra=0,
    can_delete=False
)


class ImportNilaiUploadForm(forms.Form):
    excel_file = forms.FileField(
        allow_empty_file=False, 
        validators=[validate_excel_file], 
        widget=forms.ClearableFileInput(attrs={
            'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'
        }),
        label='File Nilai (Excel)',
        help_text='Disarankan mengupload file excel dari template yang sudah disediakan.'
    )

    def clean(self):
        cleaned_data = super().clean()
        excel_file = cleaned_data.get('excel_file')

        if excel_file is None:
            raise forms.ValidationError('File tidak boleh kosong dan harus dalam format Excel (.xlsx, .xls).')

        if not excel_file.name.endswith('.xlsx'):
            raise forms.ValidationError('File harus dalam format Excel (.xlsx, .xls).')
        return cleaned_data 

