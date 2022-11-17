import django_filters as filter
from distutils.util import strtobool
from widgets.widgets import (
    MyNumberInput,
    MySearchInput,
    MySelectInput,
)
from .models import Kurikulum


KURIKULUM_IS_ACTIVE = (('', '-------'), ('true', 'Aktif'), ('false', 'Non-Aktif'))

class KurikulumFilter(filter.FilterSet):
    nama = filter.CharFilter(
        field_name='nama', 
        lookup_expr='icontains', 
        label='Nama kurikulum',
        widget=MySearchInput(
            attrs={
                'placeholder': 'Cari nama kurikulum...'
            }
        ),
    )
    tahun_mulai = filter.NumberFilter(
        field_name='tahun_mulai',
        label='Tahun mulai',
        widget=MyNumberInput,
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