from django.urls import path
from .views import(
    SemesterReadAllView,
    SemesterReadView
)


app_name = 'semester'
urlpatterns = [
    path('', SemesterReadAllView.as_view(), name='read-all'),
    path('<int:semester_kurikulum_id>', SemesterReadAllView.as_view(), name='read'),
]
