from django.urls import path
from .views import (
    RPSHomeView,
    RPSCreateView,
)


app_name = 'rps'
urlpatterns = [
    path('', RPSHomeView.as_view(), name='home'),
    path('create/', RPSCreateView.as_view(), name='create'),
]
