from django.urls import path, include
from .views import (
    MataKuliahSemesterCreateView,
    MataKuliahSemesterReadView,
    MataKuliahSemesterBulkDeleteView,

    KelasMataKuliahSemesterUpdateView,
    KelasMataKuliahSemesterDeleteView,

    PesertaMataKuliahSemesterCreateView,
    PesertaMataKuliahBulkUpdateView,
    PesertaMataKuliahBulkDeleteView,
    StudentPerformanceReadView,
    StudentPerformanceCalculateView,

    NilaiKomponenCloEditView,
    NilaiKomponenCloPesertaEditView,
    ImportNilaiMataKuliahSemesterView,

    NilaiAverageCloAchievementCalculateView,
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
    path('<int:mk_semester_id>/peserta/<int:peserta_id>/', StudentPerformanceReadView.as_view(), name='student-performance'),
    path('<int:mk_semester_id>/peserta/<int:peserta_id>/calculate/', StudentPerformanceCalculateView.as_view(), name='calculate-student-performance'),
    path('<int:mk_semester_id>/peserta/create/', PesertaMataKuliahSemesterCreateView.as_view(), name='peserta-create'),
    path('<int:mk_semester_id>/peserta/bulk-delete/', PesertaMataKuliahBulkDeleteView.as_view(), name='peserta-bulk-delete'),
    path('<int:mk_semester_id>/peserta/bulk-update/', PesertaMataKuliahBulkUpdateView.as_view(), name='peserta-bulk-update'),

    # Nilai Komponen CLO
    path('<int:mk_semester_id>/nilai/edit/', NilaiKomponenCloEditView.as_view(), name='nilai-komponen-edit'),
    path('<int:mk_semester_id>/nilai/<int:peserta_id>/hx-edit/', NilaiKomponenCloPesertaEditView.as_view(template_name='mata-kuliah-semester/partials/nilai-komponen/peserta-edit-form.html'), name='hx-nilai-komponen-peserta-edit'),
    path('<int:mk_semester_id>/nilai/<int:peserta_id>/edit/', NilaiKomponenCloPesertaEditView.as_view(template_name='mata-kuliah-semester/nilai-komponen/edit-view.html'), name='nilai-komponen-peserta-edit'),
    path('<int:mk_semester_id>/nilai/hx-import/', ImportNilaiMataKuliahSemesterView.as_view(template_name='mata-kuliah-semester/partials/nilai-komponen/import-form-modal.html'), name='hx-nilai-komponen-import'),
    path('<int:mk_semester_id>/nilai/import/', ImportNilaiMataKuliahSemesterView.as_view(template_name='mata-kuliah-semester/nilai-komponen/import-form-view.html'), name='nilai-komponen-import'),

    # Nilai Average CLO Achivement
    path('<int:mk_semester_id>/results/nilai-avg-calculate/', NilaiAverageCloAchievementCalculateView.as_view(), name='nilai-avg-calculate'),
    
    # CLO
    path('<int:mk_semester_id>/clo/', include('clo.urls')),

    # RPS
    path('<int:mk_semester_id>/rps/', include('rps.urls')),
]
