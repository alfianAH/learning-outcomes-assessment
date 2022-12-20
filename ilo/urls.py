from django.urls import path
from .views import(
    IloReadAllView,
    IloCreateHxView,
    IloBulkDeleteView,
)


app_name = 'ilo'
urlpatterns = [
    path('', IloReadAllView.as_view(), name='read-all'),
    path('hx-create/', IloCreateHxView.as_view(), name='hx-create'),
    path('bulk-delete/', IloBulkDeleteView.as_view(), name='bulk-delete'),
]
