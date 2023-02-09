from django.urls import path
from .views import (
    CloReadAllView,
    CloCreateView,
    CloBulkDeleteView,
    CloDuplicateView,
    CloReadAllGraphJsonResponse,
    CloReadView,

    KomponenCloBulkDeleteView,
    KomponenCloCreateView,
)


app_name = 'clo'
urlpatterns = [
    path('', CloReadAllView.as_view(), name='read-all'),
    path('<int:clo_id>/', CloReadView.as_view(), name='read'),
    path('create/', CloCreateView.as_view(), name='create'),
    path('duplicate/', CloDuplicateView.as_view(), name='duplicate'),
    path('bulk-delete/', CloBulkDeleteView.as_view(), name='bulk-delete'),
    path('read-all-graph/', CloReadAllGraphJsonResponse.as_view(), name='read-all-graph'),

    # Komponen CLO
    path('<int:clo_id>/bulk-delete/', KomponenCloBulkDeleteView.as_view(), name='komponen-clo-bulk-delete'),
    path('<int:clo_id>/create/', KomponenCloCreateView.as_view(), name='komponen-clo-create'),
]
