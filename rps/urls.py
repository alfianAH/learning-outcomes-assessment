from django.urls import path
from .views import (
    RPSHomeView,
    RPSCreateView,
    RPSLockView,
    RPSUnlockView,
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
    path('lock/', RPSLockView.as_view(), name='lock'),
    path('unlock/', RPSUnlockView.as_view(), name='unlock'),
]
