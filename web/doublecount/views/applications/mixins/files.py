from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from core import private_storage
from doublecount.models import DoubleCountingDocFile

from .response_serializer import ResponseSerializer


class ApplicationFileSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    link = serializers.URLField(required=False)


class ApplicationFileUploadSerializer(serializers.Serializer):
    extra_files = serializers.ListField(child=serializers.FileField(), required=False, allow_empty=True)


class ApplicationFilesMixin(RetrieveModelMixin):
    @extend_schema(
        request=ApplicationFileUploadSerializer,
        responses={200: ResponseSerializer},
    )
    @action(detail=True, methods=["POST"], url_path="upload-files")
    @transaction.atomic
    def upload_files(self, request, id=None):
        serializer = ApplicationFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dca = self.get_object()
        extra_files = serializer.validated_data.get("extra_files")

        dc_files = []
        for file in extra_files:
            s3_path = f"doublecounting/{dca.id}_file_{file.name}"
            dc_file = DoubleCountingDocFile(url=s3_path, file_name=file.name, dca=dca)
            dc_files.append(dc_file)
            private_storage.save(s3_path, file)
        DoubleCountingDocFile.objects.bulk_create(dc_files)

        return Response({"status": "success"})

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "file_id",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description="File ID to delete",
                required=True,
            ),
        ],
        responses={200: ResponseSerializer},
    )
    @action(detail=True, methods=["DELETE"], url_path="files/(?P<file_id>[^/.]+)")
    @transaction.atomic
    def delete_file(self, request, id=None, file_id=None):
        deleted_file = get_object_or_404(DoubleCountingDocFile, pk=file_id)
        private_storage.delete(deleted_file.url)
        deleted_file.delete()
        return Response({"status": "success"})
