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
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
    path('update/', RPSUpdateView.as_view(), name='update'),
    path('delete/', RPSDeleteView.as_view(), name='delete'),

    # PertemuanRPS
    path('pertemuan/<int:rps_id>/', PertemuanRPSReadView.as_view(), name='pertemuan-read'),
    path('pertemuan/create/', PertemuanRPSCreateView.as_view(), name='pertemuan-create'),
    path('pertemuan/bulk-delete/', PertemuanRPSBulkDeleteView.as_view(), name='pertemuan-bulk-delete'),
    path('pertemuan/<int:rps_id>/update/', PertemuanRPSUpdateView.as_view(), name='pertemuan-update'),
]
