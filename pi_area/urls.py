from django.urls import path
from .views import (
    PIAreaReadAllView,
    PerformanceIndicatorAreaCreateHxView,
    PerformanceIndicatorAreaReadView,
    PerformanceIndicatorAreaBulkDeleteView,
    PIAreaCreateView,
    AssessmentAreaDeleteView,
    AssessmentAreaUpdateHxView,
)


app_name = 'pi_area'
urlpatterns = [
    # PI Area
    path('', PIAreaReadAllView.as_view(), name='read-all'),
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='read'),
    path('pi-area-bulk-delete/', PerformanceIndicatorAreaBulkDeleteView.as_view(), name='pi-area-bulk-delete'),

    # Assessment Area
    path('create/', PIAreaCreateView.as_view(), name='create'),
    path('<int:assessment_area_id>/hx-pi-area-create/', PerformanceIndicatorAreaCreateHxView.as_view(), name='hx-pi-area-create'),
    path('<int:assessment_area_id>/hx-update/', AssessmentAreaUpdateHxView.as_view(), name='hx-assessment-area-update'),
    path('<int:assessment_area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='delete'),
]
