from django.urls import path
from .views import (
    PIAreaCreateView,
    AssessmentAreaDeleteView,
)


app_name = 'pi_area'
urlpatterns = [
    path('create/', PIAreaCreateView.as_view(), name='create'),
    path('<int:area_id>/delete/', AssessmentAreaDeleteView.as_view(), name='delete'),
]
