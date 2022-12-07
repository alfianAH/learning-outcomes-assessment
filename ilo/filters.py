import django_filters as filter
from django import forms
from learning_outcomes_assessment.widgets import (
    MyNumberInput,
    MyRadioInput,
    MyRangeInput,
    MySearchInput,
    MyRangeWidget,
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
    satisfactory_level = filter.RangeFilter(
        field_name='satisfactory_level',
        label='Satisfactory level',
        widget=MyRangeWidget(
            widgets=(
                MyRangeInput(attrs={
                    'placeholder': '0',
                    'min': 0,
                    'max': 100,
                }),
                MyRangeInput(attrs={
                    'placeholder': '100',
                    'min': 0,
                    'max': 100,
                })
            )
        ),
    )
    persentase_capaian_ilo = filter.RangeFilter(
        field_name='persentase_capaian_ilo',
        label='Persentase Capaian ILO',
        widget=MyRangeWidget(
            widgets=(
                MyRangeInput(attrs={
                    'placeholder': '0',
                    'min': 0,
                    'max': 100,
                }),
                MyRangeInput(attrs={
                    'placeholder': '100',
                    'min': 0,
                    'max': 100,
                })
            )
        ),
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
