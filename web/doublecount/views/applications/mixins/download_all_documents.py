import io
import zipfile

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from core import private_storage

from .response_serializer import ResponseSerializer


class DownloadAllDocumentsMixin:
    @extend_schema(
        responses={200: ResponseSerializer},
    )
    @action(detail=True, methods=["GET"], url_path="download-all")
    def download_all_documents(self, request, id=None):
        application = self.get_object()
        documents = application.documents.all()

        if not documents.exists():
            raise NotFound("Aucun document disponible")

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for doc in documents:
                # Download each document from S3 and add it to the zip file
                try:
                    file_content = private_storage.open(doc.url).read()
                    zip_file.writestr(doc.file_name, file_content)
                except FileNotFoundError:
                    continue

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="dossier_DC_{application.id}.zip"'
        return response
