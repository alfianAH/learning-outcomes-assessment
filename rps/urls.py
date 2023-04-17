from django.urls import path
from .views import (
    RPSHomeView,
    RPSCreateView,
    RPSUpdateView,
    RPSLockView,
    RPSUnlockView,
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
    path('update/', RPSUpdateView.as_view(), name='update'),
    path('lock/', RPSLockView.as_view(), name='lock'),
    path('unlock/', RPSUnlockView.as_view(), name='unlock'),
]
