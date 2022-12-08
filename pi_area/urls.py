from django.urls import path
from .views import (
    PIAreaCreateView,
)


app_name = 'pi_area'
urlpatterns = [
    path('create/', PIAreaCreateView.as_view(), name='create'),
]
