from django.urls import path
from .upload_lot_excel import upload_lot_excel

urlpatterns = [
    path("upload-lot-excel", upload_lot_excel, name="api-v5-transactions-upload-lot-excel"),
]
