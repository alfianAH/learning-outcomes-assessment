from django.urls import path
from .views import(
    IloReadAllView,
)


app_name = 'ilo'
urlpatterns = [
    path('', IloReadAllView.as_view(), name='read-all'),
]
