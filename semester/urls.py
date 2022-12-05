from django.urls import path, include
from .views import(
    SemesterReadAllView,
    SemesterReadView,
)


app_name = 'semester'
urlpatterns = [
    path('', SemesterReadAllView.as_view(), name='read-all'),
    path('<int:semester_kurikulum_id>/', SemesterReadView.as_view(), name='read'),

    # ILO
    path('<int:semester_kurikulum_id>/ilo/', include('ilo.urls')),

    # MK Semester

    # Performance Indicator
    # path('pi/', include('performance_indicators.urls')),
]
