from django.urls import path
from .views import (
    GetTahunAjaranJsonResponse,
    GetSemesterJsonResponse,
    LaporanCapaianPembelajaranView,
    LaporanCapaianPembelajaranMahasiswaView,
)


app_name = 'laporan_cpl'
urlpatterns = [
    path('', LaporanCapaianPembelajaranView.as_view(), name='home'),
    path('<str:username>/', LaporanCapaianPembelajaranMahasiswaView.as_view(), name='laporan-mhs'),
    path('formset-choices/tahun-ajaran/', GetTahunAjaranJsonResponse.as_view(), name='formset-tahun-ajaran-choices'),
    path('formset-choices/semester/', GetSemesterJsonResponse.as_view(), name='formset-semester-choices'),
]
