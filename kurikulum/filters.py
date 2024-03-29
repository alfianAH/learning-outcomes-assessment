import django_filters as filter
from django import forms
from distutils.util import strtobool
from learning_outcomes_assessment.widgets import (
    MyRangeInput,
    MyRangeWidget,
    MyRadioInput,
    MySearchInput,
    MySelectInput,
)
from .models import Kurikulum


KURIKULUM_IS_ACTIVE = (
    ('', '---------'), 
    ('true', 'Aktif'), 
    ('false', 'Non-Aktif')
)
KURIKULUM_ORDERING_BY = (
    ('nama', 'Nama'), 
    ('tahun_mulai', 'Tahun Mulai'),
    ('prodi_jenjang__jenjang_studi__kode', 'Jenjang Studi'), 
    ('is_active', 'Keaktifan')
)

class KurikulumFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='nama', 
        lookup_expr='icontains', 
        label='Nama kurikulum',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama kurikulum...',
                'autocomplete': 'off'
            }
        ),
    )
    tahun_mulai = filter.RangeFilter(
        field_name='tahun_mulai',
        label='Tahun mulai',
        widget=MyRangeWidget(
            widgets=(
                MyRangeInput(attrs={
                    'placeholder': '2010',
                }),
                MyRangeInput(attrs={
                    'placeholder': '2022',
                })
            )
        ),
    )
    is_active = filter.TypedChoiceFilter(
        field_name='is_active', 
        label='Keaktifan', 
        choices=KURIKULUM_IS_ACTIVE, 
        coerce=strtobool,
        widget=MySelectInput,
    )
    
    class Meta:
        model = Kurikulum
        fields = ('nama', 'tahun_mulai', 'is_active')


class KurikulumSort(forms.Form):
    ordering_by = forms.ChoiceField(
        choices=KURIKULUM_ORDERING_BY,
        widget=MyRadioInput,
        label='Urutkan berdasarkan',
        initial='tahun_mulai',
    )
