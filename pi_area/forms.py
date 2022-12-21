from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from learning_outcomes_assessment.widgets import (
    MyTextInput,
    MyColorSelectInput,
    MyTextareaInput
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


class PerformanceIndicatorAreaInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index) -> None:
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            form.fields['DELETE'].widget = forms.CheckboxInput(
                attrs={
                    'class': 'hidden'
                }
            )


PerformanceIndicatorAreaFormSet = inlineformset_factory(
    AssessmentArea, 
    PerformanceIndicatorArea, 
    form=PerformanceIndicatorAreaForm, 
    formset=PerformanceIndicatorAreaInlineFormSet,
    extra=0,
    can_delete=True
)

PerformanceIndicatorFormSet = inlineformset_factory(
    PerformanceIndicatorArea,
    PerformanceIndicator,
    form=PerformanceIndicatorForm,
    formset=PerformanceIndicatorAreaInlineFormSet,
    extra=0,
    can_delete=True,
)