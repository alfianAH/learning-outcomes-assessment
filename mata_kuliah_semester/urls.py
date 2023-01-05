from django.urls import path
from .views import (
    MataKuliahSemesterCreateView,
    MataKuliahSemesterUpdateView,
    MataKuliahSemesterReadView,
    MataKuliahSemesterBulkDeleteView,
)


app_name = 'mata_kuliah_semester'
urlpatterns = [
    path('<int:mk_semester_id>/', MataKuliahSemesterReadView.as_view(), name='read'),
    path('create/', MataKuliahSemesterCreateView.as_view(), name='create'),
    path('update/', MataKuliahSemesterUpdateView.as_view(), name='update'),
    path('bulk-delete/', MataKuliahSemesterBulkDeleteView.as_view(), name='bulk-delete'),
]
