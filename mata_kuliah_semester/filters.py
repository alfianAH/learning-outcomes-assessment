from django import forms
import django_filters as filter
from learning_outcomes_assessment.widgets import (
    MyNumberInput,
    MyRadioInput,
    MySearchInput,
)
from .models import (
    MataKuliahSemester,
)


MK_SEMESTER_ORDERING_BY = (
    ('mk_kurikulum__kode', 'Kode MK'),
    ('mk_kurikulum__nama', 'Nama'),
    ('mk_kurikulum__sks', 'SKS'),
)

class MataKuliahSemesterFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='mk_kurikulum__nama', 
        lookup_expr='icontains', 
        label='Nama Mata Kuliah',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama mata kuliah...',
                'autocomplete': 'off'
            }
        ),
    )
    sks = filter.NumberFilter(
        field_name='mk_kurikulum__sks',
        label='SKS',
        widget=MyNumberInput(
            attrs={
                'placeholder': 'Masukkan SKS mata kuliah'
            }
        ),
    )

    class Meta:
        model = MataKuliahSemester
        fields = ('mk_kurikulum__nama', 'mk_kurikulum__sks')


class MataKuliahSemesterSort(forms.Form):
    ordering_by = forms.ChoiceField(
        choices=MK_SEMESTER_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='mk_kurikulum__nama',
    )
