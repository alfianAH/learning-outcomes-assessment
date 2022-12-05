from django.urls import path
from .views import(
    IloReadAllView,
    IloCreateView
)


app_name = 'ilo'
urlpatterns = [
    path('', IloReadAllView.as_view(), name='read-all'),
    path('create/', IloCreateView.as_view(), name='create'),
]
