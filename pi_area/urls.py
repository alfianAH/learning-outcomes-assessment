from django.urls import include, path
from .views import (
    PIAreaCreateView,
    PIAreaReadAllView,
    PIAreaUpdateView,
    PIAreaDuplicateFormView,
    PIAreaLockView,
    PIAreaUnlockView,

    AssessmentAreaDeleteView,

    PerformanceIndicatorAreaReadView,
    PerformanceIndicatorAreaBulkDeleteView,

    PerformanceIndicatorAreaUpdateView,
)


app_name = 'pi_area'
urlpatterns = [
    #  Assessment area and PI Area
    path('', PIAreaReadAllView.as_view(), name='read-all'),
    path('hx-create/', PIAreaCreateView.as_view(template_name='pi-area/partials/pi-area-form.html'), name='hx-create'),
    path('create/', PIAreaCreateView.as_view(template_name='pi-area/pi-area-create-view.html'), name='create'),
    path('duplicate/', PIAreaDuplicateFormView.as_view(), name='duplicate'),
    path('lock/', PIAreaLockView.as_view(), name='lock'),
    path('unlock/', PIAreaUnlockView.as_view(), name='unlock'),

    path('assessment-area/<int:assessment_area_id>/hx-update/', PIAreaUpdateView.as_view(template_name='pi-area/partials/pi-area-form.html'), name='hx-update'),
    path('assessment-area/<int:assessment_area_id>/update/', PIAreaUpdateView.as_view(template_name='pi-area/pi-area-update-view.html'), name='update'),

    # PI Area
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='pi-area-read'),
    # PI Area and Performance Indicator
    path('<int:pi_area_id>/update/', PerformanceIndicatorAreaUpdateView.as_view(), name='pi-area-update'),
    path('pi-area-bulk-delete/', PerformanceIndicatorAreaBulkDeleteView.as_view(), name='pi-area-bulk-delete'),

    # Assessment Area
    path('assessment-area/<int:assessment_area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='assessment-area-delete'),
]
