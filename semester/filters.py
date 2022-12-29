import django_filters as filter
from django import forms
from learning_outcomes_assessment.widgets import (
    MyRadioInput, 
    MySearchInput,
    MySelectInput
)
from .models import (
    Semester, 
    SemesterKurikulum,
    TipeSemester,
)


SEMESTER_ORDERING_BY = (
    ('nama', 'Nama'),
    ('tahun_ajaran', 'Tahun Ajaran'),
    ('tipe_semester', 'Tipe Semester'),
)

SEMESTER_KURIKULUM_ORDERING_BY = (
    ('semester__nama', 'Nama'),
    ('semester__tahun_ajaran', 'Tahun Ajaran'),
    ('semester__tipe_semester', 'Tipe Semester'),
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
        model = SemesterKurikulum
        fields = ('semester__nama', 'semester__tipe_semester')


class SemesterSort(forms.Form):
    semester_ordering_by = forms.ChoiceField(
        choices=SEMESTER_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='nama',
    )

class SemesterProdiSort(forms.Form):
    ordering_by = forms.ChoiceField(
        choices=SEMESTER_KURIKULUM_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='semester__nama',
    )
