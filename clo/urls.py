from django.urls import path
from .views import (
    CloReadAllView,
    CloCreateView,
    CloBulkDeleteView,
)


app_name = 'clo'
urlpatterns = [
    path('', CloReadAllView.as_view(), name='read-all'),
    path('create/', CloCreateView.as_view(), name='create'),
    path('bulk-delete/', CloBulkDeleteView.as_view(), name='bulk-delete'),
]
