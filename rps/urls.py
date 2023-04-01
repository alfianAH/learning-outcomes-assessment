from django.urls import path
from .views import (
    RPSHomeView,
    RPSCreateView,
    RPSUpdateView,
    RPSDeleteView,
    RPSLockView,
    RPSUnlockView,

    RincianRPSDuplicateView,

    PertemuanRPSCreateView,
    PertemuanRPSBulkDeleteView,
    PertemuanRPSReadView,
    PertemuanRPSUpdateView,
    PertemuanRPSDuplicateView,

    RincianPertemuanRPSCreateView,
    RincianPertemuanRPSUpdateView,
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
    path('update/', RPSUpdateView.as_view(), name='update'),
    path('delete/', RPSDeleteView.as_view(), name='delete'),
    path('duplicate/', RincianRPSDuplicateView.as_view(), name='duplicate'),
    path('lock/',  RPSLockView.as_view(), name='lock'),
    path('unlock/',  RPSUnlockView.as_view(), name='unlock'),

    # PertemuanRPS
    path('pertemuan/<int:pertemuan_rps_id>/', PertemuanRPSReadView.as_view(), name='pertemuan-read'),
    path('pertemuan/create/', PertemuanRPSCreateView.as_view(), name='pertemuan-create'),
    path('pertemuan/bulk-delete/', PertemuanRPSBulkDeleteView.as_view(), name='pertemuan-bulk-delete'),
    path('pertemuan/duplicate/', PertemuanRPSDuplicateView.as_view(), name='pertemuan-duplicate'),
    path('pertemuan/<int:pertemuan_rps_id>/update/', PertemuanRPSUpdateView.as_view(), name='pertemuan-update'),

    # Rincian pertemuan RPS
    path('pertemuan/<int:pertemuan_rps_id>/rincian/create/', RincianPertemuanRPSCreateView.as_view(), name='rincian-pertemuan-create'),
    path('pertemuan/<int:pertemuan_rps_id>/rincian/update/', RincianPertemuanRPSUpdateView.as_view(), name='rincian-pertemuan-update'),
]
