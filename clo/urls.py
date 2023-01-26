from django.urls import path
from .views import (
    CloReadAllView,
)


app_name = 'clo'
urlpatterns = [
    path('', CloReadAllView.as_view(), name='read-all'),
]
