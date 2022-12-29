from django.urls import path, include
from .views import(
    SemesterReadAllView,
    SemesterReadView,
    SemesterBulkDeleteView,
)


app_name = 'semester'
urlpatterns = [
    path('', SemesterReadAllView.as_view(), name='read-all'),
    path('delete/', SemesterBulkDeleteView.as_view(), name='bulk-delete'),
    path('<int:semester_prodi_id>/', SemesterReadView.as_view(), name='read'),

    # ILO
    # path('<int:semester_prodi_id>/ilo/', include('ilo.urls')),

    # MK Semester
    path('<int:semester_prodi_id>/mk/', include('mata_kuliah.urls')),

    # Performance Indicator
    # path('<int:semester_prodi_id>/pi-area/', include('pi_area.urls')),
]
