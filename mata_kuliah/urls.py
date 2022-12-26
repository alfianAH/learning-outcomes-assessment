from django.urls import path
from .views import (
    MataKuliahSemesterReadAllView,
)


app_name = 'mata_kuliah'
urlpatterns = [
    path('', MataKuliahSemesterReadAllView.as_view(), name='read-all'),
]
