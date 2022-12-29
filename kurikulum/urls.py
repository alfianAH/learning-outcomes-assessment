from django.urls import path
from .views import (
    KurikulumReadAllSyncFormWizardView,
    KurikulumReadAllView,
    KurikulumReadView,
    KurikulumBulkUpdateView,
    KurikulumBulkDeleteView,

    MataKuliahKurikulumCreateView,
    MataKuliahKurikulumReadView,
    MataKuliahKurikulumUpdateView,
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
    path('<int:kurikulum_id>/mk/update/', MataKuliahKurikulumUpdateView.as_view(), name='mk-update'),
    path('<int:kurikulum_id>/mk/delete/', MataKuliahKurikulumBulkDeleteView.as_view(), name='mk-bulk-delete'),
]
