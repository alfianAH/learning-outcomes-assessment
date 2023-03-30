from django.urls import path
from .views import (
    RPSHomeView,
    RPSCreateView,
    RPSUpdateView,
    RPSDeleteView,

    PertemuanRPSCreateView,
    PertemuanRPSBulkDeleteView,
    PertemuanRPSReadView,
    PertemuanRPSUpdateView,

    RincianPertemuanRPSCreateView,
    RincianPertemuanRPSUpdateView,
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
    path('update/', RPSUpdateView.as_view(), name='update'),
    path('delete/', RPSDeleteView.as_view(), name='delete'),

    # PertemuanRPS
    path('pertemuan/<int:pertemuan_rps_id>/', PertemuanRPSReadView.as_view(), name='pertemuan-read'),
    path('pertemuan/create/', PertemuanRPSCreateView.as_view(), name='pertemuan-create'),
    path('pertemuan/bulk-delete/', PertemuanRPSBulkDeleteView.as_view(), name='pertemuan-bulk-delete'),
    path('pertemuan/<int:pertemuan_rps_id>/update/', PertemuanRPSUpdateView.as_view(), name='pertemuan-update'),

    # Rincian pertemuan RPS
    path('pertemuan/<int:pertemuan_rps_id>/rincian/create/', RincianPertemuanRPSCreateView.as_view(), name='rincian-pertemuan-create'),
    path('pertemuan/<int:pertemuan_rps_id>/rincian/update/', RincianPertemuanRPSUpdateView.as_view(), name='rincian-pertemuan-update'),
]
