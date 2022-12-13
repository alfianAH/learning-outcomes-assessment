from django.urls import path
from .views import (
    PerformanceIndicatorAreaReadAllView,
    PerformanceIndicatorAreaReadView,
    PerformanceIndicatorAreaBulkDelete,
    PIAreaCreateView,
    AssessmentAreaDeleteView,
)


app_name = 'pi_area'
urlpatterns = [
    # PI Area
    path('', PerformanceIndicatorAreaReadAllView.as_view(), name='read-all'),
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='read'),
    path('pi-area-bulk-delete/', PerformanceIndicatorAreaBulkDelete.as_view(), name='pi-area-bulk-delete'),

    # Assessment Area
    path('create/', PIAreaCreateView.as_view(), name='create'),
    path('<int:assessment_area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='delete'),
]
