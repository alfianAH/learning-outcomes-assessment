from django.urls import path
from .views import (
    LaporanCapaianPembelajaranView,
    GetTahunAjaranJsonResponse,
    GetSemesterJsonResponse,
)


app_name = 'laporan_cpl'
urlpatterns = [
    path('', LaporanCapaianPembelajaranView.as_view(), name='home'),
    path('formset-choices/tahun-ajaran/', GetTahunAjaranJsonResponse.as_view(), name='formset-tahun-ajaran-choices'),
    path('formset-choices/semester/', GetSemesterJsonResponse.as_view(), name='formset-semester-choices'),
]
