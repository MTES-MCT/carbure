from django.urls import path, include

urlpatterns = [
    path('public/', include('api.v3.public.urls')),
    path('lots/', include('api.v3.lots.urls')),
    path('settings/', include('api.v3.settings.urls')),
    path('admin/', include('api.v3.admin.urls')),
]
