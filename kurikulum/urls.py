from django.urls import path
from .views import (
    KurikulumReadAllView,
)


app_name = 'kurikulum'
urlpatterns = [
    path('', KurikulumReadAllView.as_view(), name='read-all'),
]
