from django.urls import path
from .views import(
    MataKuliahKurikulumReadAllView,
    MataKuliahKurikulumCreateView,
    MataKuliahKurikulumReadView,
    MataKuliahKurikulumBulkUpdateView,
    MataKuliahKurikulumBulkDeleteView,
)


app_name = 'mata_kuliah_kurikulum'
urlpatterns = [
    path('', MataKuliahKurikulumReadAllView.as_view(), name='read-all'),
    path('create/', MataKuliahKurikulumCreateView.as_view(), name='create'),
    path('<int:mk_id>/', MataKuliahKurikulumReadView.as_view(), name='read'),
    path('bulk-update/', MataKuliahKurikulumBulkUpdateView.as_view(), name='bulk-update'),
    path('bulk-delete/', MataKuliahKurikulumBulkDeleteView.as_view(), name='bulk-delete'),
]
