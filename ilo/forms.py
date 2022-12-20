from django import forms
from .models import Ilo
from pi_area.models import PerformanceIndicatorArea
from learning_outcomes_assessment.widgets import(
    MyNumberInput,
    MyTextInput,
    MyTextareaInput,
    MySelectInput
)
from random import randint


class IloCreateForm(forms.ModelForm):
    class Meta:
        model = Ilo
        fields = ['nama', 'pi_area', 'satisfactory_level', 'deskripsi']
        labels = {
            'pi_area': 'Kode area PI'
        }
        widgets = {
            'nama': MyTextInput(attrs={
                'placeholder': 'ILO {}'.format(randint(1, 5)),
            }),
            'pi_area': MySelectInput(),
            'satisfactory_level': MyNumberInput(attrs={
                'placeholder': 'Masukkan satisfactory level',
                'min': 0,
                'max': 100,
            }),
            'deskripsi': MyTextareaInput(attrs={
                'cols': 30,
                'rows': 3,
                'placeholder': 'Masukkan deskripsi',
            }),
        }

    def __init__(self, *args, **kwargs):
        semester_obj = kwargs.pop('semester_obj')
        super().__init__(*args, **kwargs)

        self.fields['pi_area'].queryset = PerformanceIndicatorArea.objects.filter(assessment_area__semester=semester_obj)
