from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from doublecount.models import DoubleCountingApplication

from .response_serializer import ResponseSerializer


class RejectDoubleCountingSerializer(serializers.Serializer):
    dca_id = serializers.PrimaryKeyRelatedField(queryset=DoubleCountingApplication.objects.all())


class RejectActionMixin:
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
        request=RejectDoubleCountingSerializer,
        responses={200: ResponseSerializer},
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False)
    def reject(self, request, id=None):
        serializer = RejectDoubleCountingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = serializer.validated_data["dca_id"]

        application.status = DoubleCountingApplication.REJECTED
        application.save()  # save before sending email, just in case

        # send_dca_status_email(application, request) TODO: uncomment when email is ready
        return Response({"status": "success"})
