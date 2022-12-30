from django.urls import path, include
from .views import (
    KurikulumReadAllSyncFormWizardView,
    KurikulumReadAllView,
    KurikulumReadView,
    KurikulumBulkUpdateView,
    KurikulumBulkDeleteView,

    MataKuliahKurikulumCreateView,
    MataKuliahKurikulumReadView,
    MataKuliahKurikulumBulkUpdateView,
    MataKuliahKurikulumBulkDeleteView,
)


app_name = 'kurikulum'
urlpatterns = [
    path('', KurikulumReadAllView.as_view(), name='read-all'),
    path('create/', KurikulumReadAllSyncFormWizardView.as_view(), name='read-all-sync'),
    path('delete/', KurikulumBulkDeleteView.as_view(), name='bulk-delete'),
    path('update/', KurikulumBulkUpdateView.as_view(), name='bulk-update'),
    path('<int:kurikulum_id>/', KurikulumReadView.as_view(), name='read'),

    # Mata Kuliah Kurikulum
    path('<int:kurikulum_id>/mk/create/', MataKuliahKurikulumCreateView.as_view(), name='mk-create'),
    path('<int:kurikulum_id>/mk/<int:mk_id>/', MataKuliahKurikulumReadView.as_view(), name='mk-read'),
    path('<int:kurikulum_id>/mk/bulk-update/', MataKuliahKurikulumBulkUpdateView.as_view(), name='mk-bulk-update'),
    path('<int:kurikulum_id>/mk/delete/', MataKuliahKurikulumBulkDeleteView.as_view(), name='mk-bulk-delete'),

    # ILO
    path('<int:kurikulum_id>/ilo/', include('ilo.urls')),

    # Performance Indicator
    path('<int:kurikulum_id>/pi-area/', include('pi_area.urls')),
]
