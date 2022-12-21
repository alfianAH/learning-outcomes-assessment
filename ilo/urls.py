from django.urls import path
from .views import(
    IloReadAllView,
    IloReadView,
    IloCreateView,
    IloBulkDeleteView,
    IloUpdateView,
)


app_name = 'ilo'
urlpatterns = [
    path('', IloReadAllView.as_view(), name='read-all'),
    path('<int:ilo_id>/', IloReadView.as_view(), name='read'),
    path('<int:ilo_id>/hx-update/', IloUpdateView.as_view(template_name='ilo/partials/ilo-update-form.html'), name='hx-update'),
    path('<int:ilo_id>/update/', IloUpdateView.as_view(template_name='ilo/ilo-update-view.html'), name='update'),
    path('hx-create/', IloCreateView.as_view(template_name='ilo/partials/ilo-create-form.html'), name='hx-create'),
    path('create/', IloCreateView.as_view(template_name='ilo/ilo-create-view.html'), name='create'),
    path('bulk-delete/', IloBulkDeleteView.as_view(), name='bulk-delete'),
]
