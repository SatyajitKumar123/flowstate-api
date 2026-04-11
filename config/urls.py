from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.core.urls')),
    path('api/auth/', include('apps.users.urls')),
    path('api/v1/', include('apps.workspaces.urls')),
    path('api/v1/', include('apps.projects.urls')),
]
