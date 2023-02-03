from django import forms
from django.forms import inlineformset_factory
from learning_outcomes_assessment.forms.formset import CanDeleteInlineFormSet
from learning_outcomes_assessment.widgets import(
    MyCheckboxInput,
    MyNumberInput,
    MySelectInput,
    MyTextInput,
    MyTextareaInput,
    MyRadioInput,
)
from kurikulum.models import Kurikulum
from mata_kuliah_semester.models import MataKuliahSemester
from .models import (
    Clo,
    KomponenClo,
)
from .utils import (
    get_pi_area_by_kurikulum_choices,
    get_pi_by_pi_area_choices,
)


class CloForm(forms.ModelForm):
    class Meta:
        model = Clo
        fields = ['nama', 'deskripsi']
        labels = {
            'nama': 'Nama CLO'
        }
        widgets = {
            'nama': MyTextInput(attrs={
                'placeholder': 'Masukkan nama CLO...',
            }),
            'deskripsi': MyTextareaInput(attrs={
                'placeholder': 'Masukkan deskripsi CLO...',
                'cols': 30,
                'rows': 3,
            })
        }
        help_texts = {
            'nama': 'Nama CLO. Contoh: <b>CLO 1</b>',
        }


class CloDuplicateForm(forms.Form):
    semester = forms.ChoiceField(
        widget=MyRadioInput(),
        label='Duplikasi Course Learning Outcomes',
    )

    def __init__(self, *args, **kwargs):
        mk_semester: MataKuliahSemester = kwargs.pop('mk_semester')
        choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)
        
        self.fields['semester'].help_text = 'Berikut adalah pilihan semester dari <b>{}</b>. Pilih salah satu semester untuk menduplikasi Course Learning Outcomes dari semester tersebut ke <b>{}</b>'.format(mk_semester.mk_kurikulum.kurikulum.nama, mk_semester.semester.semester.nama)

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
            'teknik_penilaian': MyTextInput(attrs={
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
            'persentase': 'Persentase tiap komponen CLO (0-100).'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_permitted = False


KomponenCloFormset = inlineformset_factory(
    Clo,
    KomponenClo,
    form=KomponenCloForm,
    formset=CanDeleteInlineFormSet,
    extra=1,
    can_delete=True,
)
