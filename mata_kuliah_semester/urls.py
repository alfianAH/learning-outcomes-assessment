from django.urls import path
from .views import (
    MataKuliahSemesterCreateView,
    MataKuliahSemesterReadView,
    MataKuliahSemesterBulkDeleteView,

    KelasMataKuliahSemesterUpdateView,
    KelasMataKuliahSemesterDeleteView,

    PesertaMataKuliahSemesterCreateView,
    PesertaMataKuliahBulkDeleteView,
)


app_name = 'mata_kuliah_semester'
urlpatterns = [
    path('<int:mk_semester_id>/', MataKuliahSemesterReadView.as_view(), name='read'),
    path('create/', MataKuliahSemesterCreateView.as_view(), name='create'),
    path('bulk-delete/', MataKuliahSemesterBulkDeleteView.as_view(), name='bulk-delete'),

    # Kelas MK Semester
    path('<int:mk_semester_id>/kelas/bulk-update/', KelasMataKuliahSemesterUpdateView.as_view(), name='kelas-mk-semester-bulk-update'),
    path('<int:mk_semester_id>/kelas/<int:kelas_mk_semester_id>/', KelasMataKuliahSemesterDeleteView.as_view(), name='kelas-mk-semester-delete'),
    
    # Peserta Mata Kuliah
    path('<int:mk_semester_id>/peserta/create/', PesertaMataKuliahSemesterCreateView.as_view(), name='peserta-create'),
    path('<int:mk_semester_id>/peserta/bulk-delete/', PesertaMataKuliahBulkDeleteView.as_view(), name='peserta-bulk-delete'),
]
