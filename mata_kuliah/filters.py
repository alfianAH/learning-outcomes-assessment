from django import forms
import django_filters as filter
from learning_outcomes_assessment.widgets import (
    MyNumberInput,
    MyRadioInput,
    MySearchInput,
)
from .models import (
    MataKuliahKurikulum,
    MataKuliahSemester,
)



MK_KURIKULUM_ORDERING_BY = (
    ('kode', 'Kode MK'),
    ('nama', 'Nama'),
    ('sks', 'SKS'),
)

MK_SEMESTER_ORDERING_BY = (
    ('mk_kurikulum__kode', 'Kode MK'),
    ('mk_kurikulum__nama', 'Nama'),
    ('mk_kurikulum__sks', 'SKS'),
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
        widget=MyNumberInput,
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
