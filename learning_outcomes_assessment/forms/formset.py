from django import forms
from django.forms import BaseInlineFormSet, BaseFormSet


class CanDeleteBaseFormSet(BaseFormSet):
    def add_fields(self, form, index) -> None:
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            form.fields['DELETE'].widget = forms.CheckboxInput(
                attrs={
                    'class': 'hidden'
                }
            )

class CanDeleteInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index) -> None:
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            form.fields['DELETE'].widget = forms.CheckboxInput(
                attrs={
                    'class': 'hidden'
                }
            )