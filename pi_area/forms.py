from django import forms
from django.forms import inlineformset_factory
from learning_outcomes_assessment.forms.formset import CanDeleteInlineFormSet
from learning_outcomes_assessment.widgets import (
    MyTextInput,
    MyColorSelectInput,
    MyRadioInput,
    MyTextareaInput,
)
from .models import(
    AssessmentArea,
    PerformanceIndicatorArea,
    PerformanceIndicator
)


class AssessmentAreaForm(forms.ModelForm):
    class Meta:
        model = AssessmentArea
        fields = ['nama', 'color']
        labels = {
            'nama': 'Nama area',
            'color': 'Warna',
        }
        widgets = {
            'nama': MyTextInput(attrs={
                'placeholder': 'Area: attitude, knowledge, ...'
            }),
            'color': MyColorSelectInput
        }
        help_texts = {
            'nama': 'Nama area penilaian. Contoh: <b>Attitude</b>, <b>Knowledge</b>, dll.',
            'color': 'Warna badge dari area penilaian.'
        }


class PerformanceIndicatorAreaForm(forms.ModelForm):
    class Meta:
        model = PerformanceIndicatorArea
        fields = ['pi_code']
        labels = {
            'pi_code': 'Kode PI'
        }
        widgets = {
            'pi_code': MyTextInput(attrs={
                'placeholder': 'Kode PI: A1, K1, ...'
            })
        }
        help_texts = {
            'pi_code': 'Kode PI. Contoh: <b>A1</b>, <b>A2</b>, <b>K1</b>, dll.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_permitted = False


class PerformanceIndicatorForm(forms.ModelForm):
    class Meta:
        model = PerformanceIndicator
        fields = ['deskripsi']
        widgets = {
            'deskripsi': MyTextareaInput(
                attrs={
                    'cols': 30,
                    'rows': 3,
                    'placeholder': 'Masukkan deskripsi performance indicator',
                }
            )
        }


class PIAreaDuplicateForm(forms.Form):
    kurikulum = forms.ChoiceField(
        widget=MyRadioInput(),
        label='Duplikasi Performance Indicators'
    )

    def __init__(self, *args, **kwargs):
        kurikulum_name = kwargs.pop('kurikulum_name')
        kurikulum_choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)

        self.fields['kurikulum'].choices = kurikulum_choices
        self.fields['kurikulum'].help_text = 'Berikut adalah pilihan kurikulum yang sudah memiliki performance indicator. Pilih salah satu kurikulum untuk menduplikasi performance indicator dari kurikulum tersebut ke {}.'.format(
            kurikulum_name
        )

    def clean(self):
        cleaned_data = super().clean()
        kurikulum_id = cleaned_data.get('kurikulum')
        try: 
            kurikulum_id = int(kurikulum_id)
        except ValueError:
            kurikulum_id = 0

        cleaned_data['kurikulum'] = kurikulum_id

        return cleaned_data


PerformanceIndicatorAreaFormSet = inlineformset_factory(
    AssessmentArea, 
    PerformanceIndicatorArea, 
    form=PerformanceIndicatorAreaForm, 
    formset=CanDeleteInlineFormSet,
    extra=0,
    can_delete=True
)

PerformanceIndicatorFormSet = inlineformset_factory(
    PerformanceIndicatorArea,
    PerformanceIndicator,
    form=PerformanceIndicatorForm,
    formset=CanDeleteInlineFormSet,
    extra=0,
    can_delete=True,
)