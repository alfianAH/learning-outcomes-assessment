from django.urls import path
from .views import (
    MataKuliahSemesterReadAllHxView,
    MataKuliahSemesterCreateView,
    MataKuliahSemesterUpdateView,
    MataKuliahSemesterReadView,
)


app_name = 'mata_kuliah_semester'
urlpatterns = [
    path('hx/', MataKuliahSemesterReadAllHxView.as_view(), name='hx-read-all'),
    path('<int:mk_semester_id>/', MataKuliahSemesterReadView.as_view(), name='read'),
    path('create/', MataKuliahSemesterCreateView.as_view(), name='create'),
    path('update/', MataKuliahSemesterUpdateView.as_view(), name='update'),
]
