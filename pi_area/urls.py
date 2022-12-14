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
    #  Assessment area and PI Area
    path('', PIAreaReadAllView.as_view(), name='read-all'),
    path('create/', PIAreaCreateView.as_view(), name='create'),

    # PI Area
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='pi-area-read'),
    path('<int:assessment_area_id>/hx-pi-area-create/', PerformanceIndicatorAreaCreateHxView.as_view(), name='hx-pi-area-create'),
    path('pi-area-bulk-delete/', PerformanceIndicatorAreaBulkDeleteView.as_view(), name='pi-area-bulk-delete'),

    # Assessment Area
    path('<int:assessment_area_id>/hx-update/', AssessmentAreaUpdateHxView.as_view(), name='hx-assessment-area-update'),
    path('<int:assessment_area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='assessment-area-delete'),
]
