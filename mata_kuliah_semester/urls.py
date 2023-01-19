from django.urls import path
from .views import (
    MataKuliahSemesterCreateView,
    MataKuliahSemesterReadView,
    MataKuliahSemesterBulkDeleteView,

    KelasMataKuliahSemesterUpdateView,
    KelasMataKuliahSemesterDeleteView,
)


app_name = 'mata_kuliah_semester'
urlpatterns = [
    path('<int:mk_semester_id>/', MataKuliahSemesterReadView.as_view(), name='read'),
    path('create/', MataKuliahSemesterCreateView.as_view(), name='create'),
    path('bulk-delete/', MataKuliahSemesterBulkDeleteView.as_view(), name='bulk-delete'),

    # Kelas MK Semester
    path('<int:mk_semester_id>/update/', KelasMataKuliahSemesterUpdateView.as_view(), name='update'),
    path('<int:mk_semester_id>/kelas/<int:kelas_mk_semester_id>/', KelasMataKuliahSemesterDeleteView.as_view(), name='kelas-mk-semester-delete'),
]
