import django_filters as filter
from django import forms
from learning_outcomes_assessment.widgets import (
    MyNumberInput,
    MyRadioInput,
    MySearchInput,
    MySelectInput,
)
from .models import Ilo


ILO_ORDERING_BY = (
    ('nama', 'Nama'), 
    ('satisfactory_level', 'Satisfactory level'), 
    ('persentase_capaian_ilo', 'Persentase Capaian ILO')
)

class IloFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='nama', 
        lookup_expr='icontains', 
        label='Nama ILO',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama ILO...',
                'autocomplete': 'off'
            }
        ),
    )
    satisfactory_level = filter.NumberFilter(
        field_name='satisfactory_level',
        label='Satisfactory level',
        widget=MyNumberInput,
    )
    persentase_capaian_ilo = filter.NumberFilter(
        field_name='persentase_capaian_ilo',
        label='Persentase Capaian ILO',
        widget=MyNumberInput,
    )
    
    class Meta:
        model = Ilo
        fields = ('nama', 'satisfactory_level', 'persentase_capaian_ilo')


class IloSort(forms.Form):
    ordering_by = forms.ChoiceField(
        choices=ILO_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='nama',
    )
