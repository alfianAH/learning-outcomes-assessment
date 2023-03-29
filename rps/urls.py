from django.urls import path
from .views import (
    RPSHomeView,
    RPSCreateView,
    RPSUpdateView,
    RPSDeleteView,
    PertemuanRPSCreateView,
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
    path('update/', RPSUpdateView.as_view(), name='update'),
    path('delete/', RPSDeleteView.as_view(), name='delete'),

    # PertemuanRPS
    path('pertemuan/create/', PertemuanRPSCreateView.as_view(), name='pertemuan-create'),
]
