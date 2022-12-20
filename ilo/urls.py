from django.urls import path
from .views import(
    IloReadAllView,
    IloCreateView,
    IloBulkDeleteView,
)


app_name = 'ilo'
urlpatterns = [
    path('', IloReadAllView.as_view(), name='read-all'),
    path('hx-create/', IloCreateView.as_view(template_name='ilo/partials/ilo-create-form.html'), name='hx-create'),
    path('create/', IloCreateView.as_view(template_name='ilo/ilo-create-view.html'), name='create'),
    path('bulk-delete/', IloBulkDeleteView.as_view(), name='bulk-delete'),
]
