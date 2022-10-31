from django.shortcuts import render
from django.views.generic.list import ListView

from kurikulum.models import Kurikulum


# Create your views here.
class KurikulumReadAllView(ListView):
    model = Kurikulum
    paginate_by: int = 10
    template_name: str = 'kurikulum/home.html'
    ordering: list[str] = ['tahun_mulai']
