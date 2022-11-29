import django_filters as filter
from django import forms
from learning_outcomes_assessment.widgets import (
    MyRadioInput, 
    MySearchInput,
    MySelectInput
)
from .models import Semester, TipeSemester


SEMESTER_ORDERING_BY = (
    ('nama', 'Nama'),
    ('tahun_ajaran', 'Tahun Ajaran'),
    ('tipe_semester', 'Tipe Semester'),
)

class SemesterFilter(filter.FilterSet):
    semester_nama = filter.CharFilter(
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
    semester_tipe_semester = filter.ChoiceFilter(
        field_name='tipe_semester',
        label='Tipe Semester',
        choices=TipeSemester.choices,
        widget=MySelectInput,
    )

    class Meta:
        model = Semester
        fields = ('nama', 'tipe_semester')


class SemesterSort(forms.Form):
    semester_ordering_by = forms.ChoiceField(
        choices=SEMESTER_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='nama',
    )
