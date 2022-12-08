from django import forms
from learning_outcomes_assessment.widgets import MyTextInput
from .models import(
    AssessmentArea,
    PerformanceIndicatorArea,
)


class AssessmentAreaForm(forms.ModelForm):
    class Meta:
        model = AssessmentArea
        fields = ['nama']
        labels = {
            'nama': 'Nama area'
        }
        widgets = {
            'nama': MyTextInput(attrs={
                'placeholder': 'Area: attitude, knowledge, ...'
            })
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
