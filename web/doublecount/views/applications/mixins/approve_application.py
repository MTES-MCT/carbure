from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from certificates.models import DoubleCountingRegistration
from doublecount.helpers import send_dca_status_email
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction

from .response_serializer import ResponseSerializer


class DoubleCountingApplicationApproveError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    QUOTAS_NOT_APPROVED = "QUOTAS_NOT_APPROVED"


class ApproveDoubleCountingSerializer(serializers.Serializer):
    dca_id = serializers.PrimaryKeyRelatedField(queryset=DoubleCountingApplication.objects.all())


class ApproveActionMixin:
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
        request=ApproveDoubleCountingSerializer,
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
    @action(methods=["post"], detail=False, url_path="approve")
    def approve(self, request, id=None):
        serializer = ApproveDoubleCountingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = serializer.validated_data["dca_id"]

        remaining_quotas_to_check = DoubleCountingProduction.objects.filter(dca=application, approved_quota=-1).count()

        if remaining_quotas_to_check > 0:
            raise ValidationError({"message": DoubleCountingApplicationApproveError.QUOTAS_NOT_APPROVED})

        application.status = DoubleCountingApplication.ACCEPTED
        application.save()  # save before sending email, just in case

        # create Agreement

        production_site_address = (
            application.production_site.address
            + " "
            + application.production_site.city
            + " "
            + application.production_site.postal_code
            + " "
            + application.production_site.country.name
        )

        if not DoubleCountingRegistration.objects.filter(certificate_id=application.certificate_id).exists():
            try:
                DoubleCountingRegistration.objects.update_or_create(
                    certificate_id=application.certificate_id,
                    certificate_holder=application.producer.name,  # TO DELETE replaced by production_site.producer.name
                    production_site=application.production_site,
                    registered_address=production_site_address,  # TO DELETE replaced by production_site.address
                    valid_from=application.period_start,
                    valid_until=application.period_end,
                    application=application,
                )
            except Exception:
                raise ValidationError({"message": "Error while creating Agreement"})

        send_dca_status_email(application, request)
        return Response({"status": "success"})
