from django.urls import path, include

urlpatterns = [
    path('v3/', include('api.v3.urls')),
]
