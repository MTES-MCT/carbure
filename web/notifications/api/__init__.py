from django.urls import path, include
from .notifications import get_notifications
from .ack import ack_notifications

urlpatterns = [
    path("", get_notifications, name="notifications"),
    path("ack", ack_notifications, name="notifications-ack"),
]
