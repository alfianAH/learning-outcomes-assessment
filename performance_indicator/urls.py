from django.urls import path, include
from .views import (
    PerformanceIndicatorAreaReadAllView,
    PerformanceIndicatorAreaReadView,
)


app_name = 'performance_indicator'
urlpatterns = [
    path('', PerformanceIndicatorAreaReadAllView.as_view(), name='read-all'),
    path('<int:pi_area_id>/', PerformanceIndicatorAreaReadView.as_view(), name='read'),

    # PI Area
    path('area/', include('pi_area.urls')),
]
