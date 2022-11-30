from django import forms
import django_filters as filter
from learning_outcomes_assessment.widgets import (
    MyNumberInput,
    MyRadioInput,
    MySearchInput,
)
from .models import MataKuliahKurikulum



MK_KURIKULUM_ORDERING_BY = (
    ('kode', 'Kode MK'),
    ('nama', 'Nama'),
    ('sks', 'SKS'),
)

class MataKuliahKurikulumFilter(filter.FilterSet):
    mk_nama = filter.CharFilter(
        field_name='nama', 
        lookup_expr='icontains', 
        label='Nama Mata Kuliah',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama mata kuliah...',
                'autocomplete': 'off'
            }
        ),
    )
    mk_sks = filter.NumberFilter(
        field_name='sks',
        label='SKS',
        widget=MyNumberInput,
    )

    class Meta:
        model = MataKuliahKurikulum
        fields = ('nama', 'sks')


class MataKuliahKurikulumSort(forms.Form):
    mk_ordering_by = forms.ChoiceField(
        choices=MK_KURIKULUM_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='nama',
    )
