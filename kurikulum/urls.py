from django.urls import path
from .views import (
    KurikulumReadAllSyncFormWizardView,
    KurikulumReadSyncView,
    KurikulumReadAllView,
    KurikulumReadView,
    KurikulumDeleteView,
    KurikulumBulkDeleteView,

    MataKuliahKurikulumReadAllView,
    MataKuliahKurikulumReadView,
    MataKuliahKurikulumDeleteView,
)


app_name = 'kurikulum'
urlpatterns = [
    path('', KurikulumReadAllView.as_view(), name='read-all'),
    path('sync/', KurikulumReadAllSyncFormWizardView.as_view(), name='read-all-sync'),
    path('delete/', KurikulumBulkDeleteView.as_view(), name='bulk-delete'),
    path('<int:kurikulum_id>/sync/', KurikulumReadSyncView.as_view(), name='read-sync'),
    path('<int:kurikulum_id>/', KurikulumReadView.as_view(), name='read'),
    path('<int:kurikulum_id>/delete/', KurikulumDeleteView.as_view(), name='delete'),

    # Mata Kuliah Kurikulum
    path('<int:kurikulum_id>/mk/', MataKuliahKurikulumReadAllView.as_view(), name='mk-read-all'),
    path('<int:kurikulum_id>/mk/<int:mk_id>/', MataKuliahKurikulumReadView.as_view(), name='mk-read'),
    path('<int:kurikulum_id>/mk/<int:mk_id>/delete/', MataKuliahKurikulumDeleteView.as_view(), name='mk-delete'),
]
