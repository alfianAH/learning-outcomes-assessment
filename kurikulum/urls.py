from django.urls import path
from .views import (
    KurikulumReadAllSyncFormWizardView,
    KurikulumReadSyncView,
    KurikulumReadAllView,
    KurikulumReadView,
    KurikulumBulkUpdateView,
    KurikulumBulkDeleteView,

    MataKuliahKurikulumReadView,
    MataKuliahKurikulumBulkDeleteView,

    SemesterKurikulumBulkDeleteView,
)


app_name = 'kurikulum'
urlpatterns = [
    path('', KurikulumReadAllView.as_view(), name='read-all'),
    path('create/', KurikulumReadAllSyncFormWizardView.as_view(), name='read-all-sync'),
    path('delete/', KurikulumBulkDeleteView.as_view(), name='bulk-delete'),
    path('update/', KurikulumBulkUpdateView.as_view(), name='bulk-update'),
    path('<int:kurikulum_id>/sync/', KurikulumReadSyncView.as_view(), name='read-sync'),
    path('<int:kurikulum_id>/', KurikulumReadView.as_view(), name='read'),

    # Mata Kuliah Kurikulum
    path('<int:kurikulum_id>/mk/delete/', MataKuliahKurikulumBulkDeleteView.as_view(), name='mk-bulk-delete'),
    path('<int:kurikulum_id>/mk/<int:mk_id>/', MataKuliahKurikulumReadView.as_view(), name='mk-read'),

    # Semester Kurikulum
    path('<int:kurikulum_id>/semester/delete/', SemesterKurikulumBulkDeleteView.as_view(), name='semester-bulk-delete'),
]
