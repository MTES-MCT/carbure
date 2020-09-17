from django.urls import path, include

urlpatterns = [
    path('v3/', include('api.v3.urls')),
    path('v2/', include('api.v2.urls')),
    path('v1/', include('api.v1.urls')),
]
