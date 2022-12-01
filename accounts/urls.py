from django.urls import path

from .views import (
    login_view,
    login_oauth_view,
    logout_view,
    oauth_callback,
)

app_name = 'accounts'
urlpatterns = [
    path('login/', login_view, name='login'),
    path('login/oauth/', login_oauth_view, name='oauth'),
    path('login/oauth/callback', oauth_callback, name='oauth-callback'),
    path('logout/', logout_view, name='logout'),
]
