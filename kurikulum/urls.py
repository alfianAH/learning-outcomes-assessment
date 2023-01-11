from django.urls import path, include
from .views import (
    KurikulumCreateFormWizardView,
    KurikulumReadAllView,
    KurikulumReadView,
    KurikulumBulkUpdateView,
    KurikulumBulkDeleteView,
)


app_name = 'kurikulum'
urlpatterns = [
    path('', KurikulumReadAllView.as_view(), name='read-all'),
    path('create/', KurikulumCreateFormWizardView.as_view(), name='create'),
    path('delete/', KurikulumBulkDeleteView.as_view(), name='bulk-delete'),
    path('update/', KurikulumBulkUpdateView.as_view(), name='bulk-update'),
    path('<int:kurikulum_id>/', KurikulumReadView.as_view(), name='read'),

    # Mata Kuliah Kurikulum
    path('<int:kurikulum_id>/mk/', include('mata_kuliah_kurikulum.urls')),
    # ILO
    path('<int:kurikulum_id>/ilo/', include('ilo.urls')),
    # Performance Indicator
    path('<int:kurikulum_id>/pi-area/', include('pi_area.urls')),
]
