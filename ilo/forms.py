from django import forms
from .models import Ilo
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
