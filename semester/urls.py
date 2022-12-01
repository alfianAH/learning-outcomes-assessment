from django.urls import path
from .views import(
    SemesterHomeView,
)


app_name = 'semester'
urlpatterns = [
    path('', SemesterHomeView.as_view(), name='read-all'),
]
