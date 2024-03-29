import django_filters as filter
from django import forms
from learning_outcomes_assessment.widgets import (
    MyRadioInput,
    MyRangeInput,
    MySearchInput,
    MyRangeWidget,
)
from .models import Ilo


ILO_ORDERING_BY = (
    ('nama', 'Nama'), 
    ('satisfactory_level', 'Satisfactory level'),
)

class IloFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='nama', 
        lookup_expr='icontains', 
        label='Nama CPL',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama CPL...',
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
    
    class Meta:
        model = Ilo
        fields = ('nama', 'satisfactory_level')


class IloSort(forms.Form):
    ordering_by = forms.ChoiceField(
        choices=ILO_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='nama',
    )
