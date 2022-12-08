from django.urls import path, include
from .views import (
    PerformanceIndicatorAreaReadAllView,
)


app_name = 'performance_indicator'
urlpatterns = [
    path('', PerformanceIndicatorAreaReadAllView.as_view(), name='read-all'),

    # PI Area
    path('area/', include('pi_area.urls')),
]
