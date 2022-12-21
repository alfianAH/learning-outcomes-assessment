from django.urls import include, path
from .views import (
    PIAreaCreateView,
    PIAreaReadAllView,
    PIAreaUpdateView,

    AssessmentAreaDeleteView,

    PerformanceIndicatorAreaReadView,
    PerformanceIndicatorAreaBulkDeleteView,

    PerformanceIndicatorCreateView,
)


app_name = 'pi_area'
urlpatterns = [
    #  Assessment area and PI Area
    path('', PIAreaReadAllView.as_view(), name='read-all'),
    path('hx-create/', PIAreaCreateView.as_view(template_name='pi-area/partials/pi-area-form.html'), name='hx-create'),
    path('create/', PIAreaCreateView.as_view(template_name='pi-area/pi-area-create-view.html'), name='create'),

    path('assessment-area/<int:assessment_area_id>/hx-update/', PIAreaUpdateView.as_view(template_name='pi-area/partials/pi-area-form.html'), name='hx-update'),
    path('assessment-area/<int:assessment_area_id>/update/', PIAreaUpdateView.as_view(template_name='pi-area/pi-area-update-view.html'), name='update'),

    # PI Area
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='pi-area-read'),
    path('pi-area-bulk-delete/', PerformanceIndicatorAreaBulkDeleteView.as_view(), name='pi-area-bulk-delete'),

    # Assessment Area
    path('assessment-area/<int:assessment_area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='assessment-area-delete'),

    # Performance Indicator
    path('<int:pi_area_id>/pi/create/', PerformanceIndicatorCreateView.as_view(), name='pi-create'),
]
