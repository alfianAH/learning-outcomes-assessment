from django import forms
import django_filters as filter
from learning_outcomes_assessment.widgets import (
    MyNumberInput,
    MyRadioInput,
    MyRangeWidget, MyRangeInput,
    MySearchInput,
)
from .models import (
    MataKuliahSemester,
    NilaiMataKuliahMahasiswa,
)


MK_SEMESTER_ORDERING_BY = (
    ('mk_kurikulum__kode', 'Kode MK'),
    ('mk_kurikulum__nama', 'Nama'),
    ('mk_kurikulum__sks', 'SKS'),
)

PESERTA_MK_ORDERING_BY = (
    ('mahasiswa__username', 'NIM'),
    ('mahasiswa__name', 'Nama'),
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


class PesertaMataKuliahFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='peserta__mahasiswa__name',
        lookup_expr='icontains', 
        label='Nama mahasiswa',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama mahasiswa...',
                'autocomplete': 'off'
            }
        ),
    )

    nilai_akhir = filter.RangeFilter(
        field_name='nilai_akhir',
        label='Nilai akhir',
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
        model = NilaiMataKuliahMahasiswa
        fields = ('nilai_akhir', 'peserta__mahasiswa__name')


class PesertaMataKuliahSortForm(forms.Form):
    ordering_by = forms.ChoiceField(
        choices=PESERTA_MK_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='mahasiswa__username',
    )
