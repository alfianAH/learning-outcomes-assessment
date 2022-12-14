from django.urls import path
from .views import (
    PIAreaReadAllView,
    PerformanceIndicatorAreaReadView,
    PerformanceIndicatorAreaBulkDeleteView,
    PIAreaCreateView,
    AssessmentAreaDeleteView,
)


app_name = 'pi_area'
urlpatterns = [
    # PI Area
    path('', PIAreaReadAllView.as_view(), name='read-all'),
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='read'),
    path('pi-area-bulk-delete/', PerformanceIndicatorAreaBulkDeleteView.as_view(), name='pi-area-bulk-delete'),

    # Assessment Area
    path('create/', PIAreaCreateView.as_view(), name='create'),
    path('<int:assessment_area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='delete'),
]
