from django.urls import path, include
from .views import(
    SemesterReadAllView,
    SemesterReadView,
    SemesterCreateView,
    SemesterBulkUpdateView,
    SemesterBulkDeleteView,
)


app_name = 'semester'
urlpatterns = [
    path('', SemesterReadAllView.as_view(), name='read-all'),
    path('delete/', SemesterBulkDeleteView.as_view(), name='bulk-delete'),
    path('create/', SemesterCreateView.as_view(), name='create'),
    path('bulk-update/', SemesterBulkUpdateView.as_view(), name='bulk-update'),
    path('<int:semester_prodi_id>/', SemesterReadView.as_view(), name='read'),

    # MK Semester
    path('<int:semester_prodi_id>/mk/', include('mata_kuliah_semester.urls')),
]
