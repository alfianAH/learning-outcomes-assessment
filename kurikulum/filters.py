from django_filters import FilterSet
from .models import Kurikulum


class KurikulumFilter(FilterSet):
    class Meta:
        model = Kurikulum
        fields = ('nama', 'tahun_mulai', 'is_active')