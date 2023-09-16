from django.urls import path
from .views import (
    GetTahunAjaranJsonResponse,
    GetSemesterJsonResponse,
    LaporanCapaianPembelajaranView,
    LaporanCapaianPembelajaranDownloadView,
    LaporanCapaianPembelajaranRawDownloadView,
    LaporanCapaianPembelajaranMahasiswaView,
    LaporanCapaianPembelajaranMahasiswaDownloadView,
    LaporanCapaianPembelajaranMahasiswaRawDownloadView,

    ListMahasiswaLaporanCPLProgrmStudiView,

    LaporanPerformanceIndicatorView,
    ListPiLaporanPiView,
)


app_name = 'laporan_cpl'
urlpatterns = [
    path('', LaporanCapaianPembelajaranView.as_view(), name='home'),
    path('mahasiswa-task/', ListMahasiswaLaporanCPLProgrmStudiView.as_view(), name='list-mahasiswa'),
    path('download/', LaporanCapaianPembelajaranDownloadView.as_view(), name='download'),
    path('raw-download/', LaporanCapaianPembelajaranRawDownloadView.as_view(), name='raw-download'),
    path('laporan-pi/', LaporanPerformanceIndicatorView.as_view(), name='laporan-pi'),
    path('list-result-pi/', ListPiLaporanPiView.as_view(), name='list-result-pi'),
    
    path('<str:username>/', LaporanCapaianPembelajaranMahasiswaView.as_view(), name='laporan-mahasiswa'),
    path('<str:username>/download/', LaporanCapaianPembelajaranMahasiswaDownloadView.as_view(), name='laporan-mahasiswa-download'),
    path('<str:username>/raw-download/', LaporanCapaianPembelajaranMahasiswaRawDownloadView.as_view(), name='raw-laporan-mahasiswa-download'),
    path('formset-choices/tahun-ajaran/', GetTahunAjaranJsonResponse.as_view(), name='formset-tahun-ajaran-choices'),
    path('formset-choices/semester/', GetSemesterJsonResponse.as_view(), name='formset-semester-choices'),
]
