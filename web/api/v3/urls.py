from django.urls import path, include

urlpatterns = [
    path('common/', include('api.v3.common.urls')),
    path('lots/', include('api.v3.lots.urls')),
    path('stocks/', include('api.v3.stocks.urls')),
    path('settings/', include('api.v3.settings.urls')),
    path('admin/', include('api.v3.admin.urls')),
]
