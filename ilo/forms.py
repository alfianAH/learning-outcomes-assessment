from django import forms
from .models import Ilo
from learning_outcomes_assessment.widgets import(
    MyNumberInput,
    MyTextInput,
    MyTextareaInput,
)


class IloCreateForm(forms.ModelForm):
    class Meta:
        model = Ilo
        fields = ['nama', 'satisfactory_level', 'deskripsi']
        widgets = {
            'nama': MyTextInput(),
            'deskripsi': MyTextareaInput(attrs={
                'cols': 30,
                'rows': 5
            }),
            'satisfactory_level': MyNumberInput(),
        }
