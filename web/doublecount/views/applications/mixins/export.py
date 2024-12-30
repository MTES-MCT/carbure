import os

import boto3
from django.http import HttpResponse
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import action

from doublecount.serializers import DoubleCountingApplicationSerializer


class ExportActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="csv file.*",
                request_only=False,
                response_only=True,
                media_type="application/force-download",
            ),
        ],
        responses={
            (200, "application/force-download"): OpenApiTypes.STR,
        },
    )
    @action(methods=["get"], detail=True)
    def export(self, request, id=None):
        application = self.get_object()
        serializer = DoubleCountingApplicationSerializer(application)
        f = serializer.data["documents"][0]
        filename = f["file_name"]
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_S3_REGION_NAME"],
            endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
            use_ssl=os.environ["AWS_S3_USE_SSL"],
        )
        filepath = "/tmp/%s" % filename
        s3filepath = "{year}/{entity}/{filename}".format(
            year=application.period_start.year,
            entity=application.producer.name,
            filename=filename,
        )
        with open(filepath, "wb") as file:
            s3.download_fileobj(os.environ["AWS_DCDOCS_STORAGE_BUCKET_NAME"], s3filepath, file)
        with open(filepath, "rb") as file:
            data = file.read()
            ctype = "application/force-download"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (filename)
        return response
