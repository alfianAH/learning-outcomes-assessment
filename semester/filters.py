import django_filters as filter
from django import forms
from learning_outcomes_assessment.widgets import (
    MyRadioInput, 
    MySearchInput,
    MySelectInput,
    MyCheckboxInput,
)
from .models import (
    Semester,
    SemesterProdi,
    TipeSemester,
)


SEMESTER_ORDERING_BY = (
    ('nama', 'Nama'),
    ('tahun_ajaran', 'Tahun Ajaran'),
    ('tipe_semester', 'Tipe Semester'),
)

SEMESTER_PRODI_ORDERING_BY = (
    ('tahun_ajaran_prodi__prodi_jenjang__jenjang_studi__kode', 'Jenjang studi'),
    ('-semester__tahun_ajaran', 'Tahun Ajaran'),
    ('-semester__tipe_semester', 'Tipe Semester'),
    ('semester__nama', 'Nama'),
)

class SemesterFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='nama', 
        lookup_expr='icontains', 
        label='Nama Semester',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama semester...',
                'autocomplete': 'off'
            }
        ),
    )
    tipe_semester = filter.ChoiceFilter(
        field_name='tipe_semester',
        label='Tipe Semester',
        choices=TipeSemester.choices,
        widget=MySelectInput,
    )

    class Meta:
        model = Semester
        fields = ('nama', 'tipe_semester')


class SemesterProdiFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='semester__nama', 
        lookup_expr='icontains', 
        label='Nama Semester',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama semester...',
                'autocomplete': 'off'
            }
        ),
    )
    tipe_semester = filter.ChoiceFilter(
        field_name='semester__tipe_semester',
        label='Tipe Semester',
        choices=TipeSemester.choices,
        widget=MySelectInput,
    )

    class Meta:
        model = SemesterProdi
        fields = ('semester__nama', 'semester__tipe_semester')


class SemesterProdiSort(forms.Form):
    ordering_by = forms.MultipleChoiceField(
        choices=SEMESTER_PRODI_ORDERING_BY,
        widget=MyCheckboxInput,
        label='Urutkan berdasarkan',
        initial='semester__nama',
    )
