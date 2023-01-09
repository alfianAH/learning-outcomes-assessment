from django.urls import path

from .views import (
    login_view,
    login_oauth_view,
    logout_view,
    oauth_callback,
    ProgramStudiReadView,
    ProgramStudiBulkUpdateView,
    ProgramStudiJenjangBulkDeleteView,
)

app_name = 'accounts'
urlpatterns = [
    path('login/', login_view, name='login'),
    path('login/oauth/', login_oauth_view, name='oauth'),
    path('login/oauth/callback', oauth_callback, name='oauth-callback'),
    path('logout/', logout_view, name='logout'),

    path('prodi/<int:prodi_id>/', ProgramStudiReadView.as_view(), name='prodi-read'),
    path('prodi/<int:prodi_id>/create', ProgramStudiReadView.as_view(), name='prodi-create'),
    path('prodi/<int:prodi_id>/update/', ProgramStudiBulkUpdateView.as_view(), name='prodi-bulk-update'),
    path('prodi/<int:prodi_id>/bulk-delete', ProgramStudiJenjangBulkDeleteView.as_view(), name='prodi-jenjang-bulk-delete'),
]
