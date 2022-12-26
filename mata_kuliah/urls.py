from django.urls import path
from .views import (
    MataKuliahSemesterReadAllView,
    MataKuliahSemesterCreateView,
    MataKuliahSemesterUpdateView,
    MataKuliahSemesterReadView,
)


app_name = 'mata_kuliah'
urlpatterns = [
    path('', MataKuliahSemesterReadAllView.as_view(), name='read-all'),
    path('<int:mk_semester_id>/', MataKuliahSemesterReadView.as_view(), name='read'),
    path('create/', MataKuliahSemesterCreateView.as_view(), name='create'),
    path('update/', MataKuliahSemesterUpdateView.as_view(), name='update'),
]
