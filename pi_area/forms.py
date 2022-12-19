from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from learning_outcomes_assessment.widgets import (
    MyTextInput,
    MyColorSelectInput
)
from .models import(
    AssessmentArea,
    PerformanceIndicatorArea,
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


class PerformanceIndicatorInlineFormSet(BaseInlineFormSet):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for form in self.forms:
    #         form.empty_permitted = False

    def clean(self) -> None:
        super().clean()

        for form in self.forms:
            print(form.cleaned_data)


PerformanceIndicatorAreaFormSet = inlineformset_factory(
    AssessmentArea, 
    PerformanceIndicatorArea, 
    form=PerformanceIndicatorAreaForm, 
    formset=PerformanceIndicatorInlineFormSet,
    extra=0,
    can_delete=False
)