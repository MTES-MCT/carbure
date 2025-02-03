import traceback

from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from certificates.models import DoubleCountingRegistration
from core.carburetypes import CarbureError
from core.models import Entity
from doublecount.helpers import (
    load_dc_filepath,
    load_dc_period,
    load_dc_production_data,
    load_dc_production_history_data,
    load_dc_sourcing_data,
    load_dc_sourcing_history_data,
    send_dca_confirmation_email,
)
from doublecount.models import (
    DoubleCountingApplication,
    DoubleCountingProduction,
    DoubleCountingSourcing,
)
from doublecount.parser.dc_parser import parse_dc_excel
from transactions.models import ProductionSite

from .response_serializer import ResponseSerializer


class DoubleCountingAddError:
    AGREEMENT_ALREADY_EXISTS = "AGREEMENT_ALREADY_EXISTS"
    AGREEMENT_NOT_FOUND = "AGREEMENT_NOT_FOUND"
    APPLICATION_ALREADY_EXISTS = "APPLICATION_ALREADY_EXISTS"
    APPLICATION_ALREADY_RECEIVED = "APPLICATION_ALREADY_RECEIVED"
    MISSING_FILE = "MISSING_FILE"
    PRODUCTION_SITE_ADDRESS_UNDEFINED = "PRODUCTION_SITE_ADDRESS_UNDEFINED"


class DoubleCountingAdminAddSerializer(serializers.Serializer):
    certificate_id = serializers.CharField(required=False, allow_blank=True)
    entity_id = serializers.IntegerField()
    producer_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.filter(entity_type=Entity.PRODUCER))
    production_site_id = serializers.PrimaryKeyRelatedField(queryset=ProductionSite.objects.all())
    should_replace = serializers.BooleanField(required=False, default=False)
    file = serializers.FileField()


class AddActionMixin:
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
        request=DoubleCountingAdminAddSerializer,
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
    @transaction.atomic
    def add(self, request, *args, **kwargs):
        return self.add_application_by_type(request, Entity.ADMIN)

    def add_application_by_type(self, request, entity_type):
        serializer = DoubleCountingAdminAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producer = serializer.validated_data["producer_id"]
        should_replace = serializer.validated_data.get("should_replace")
        production_site = serializer.validated_data["production_site_id"]
        certificate_id_to_link = serializer.validated_data.get("certificate_id")
        file = serializer.validated_data.get("file")

        if entity_type == Entity.PRODUCER:
            entity_id = serializer.validated_data["entity_id"]
            if producer.id != entity_id:
                raise ValidationError({"message": CarbureError.ENTITY_NOT_ALLOWED})
        elif entity_type == Entity.ADMIN:
            certificate_id_to_link = certificate_id_to_link

        if not production_site.address or not production_site.city or not production_site.postal_code:
            raise ValidationError({"message": DoubleCountingAddError.PRODUCTION_SITE_ADDRESS_UNDEFINED})

        if file is None:
            raise ValidationError({"message": DoubleCountingAddError.MISSING_FILE})

        # 1 - load dc Data
        filepath = load_dc_filepath(file)

        (
            info,
            sourcing_forecast_rows,
            production_max_rows,
            production_forecast_rows,
            requested_quota_rows,
            sourcing_history_rows,
            production_max_history_rows,
            production_effective_history_rows,
        ) = parse_dc_excel(filepath)

        start, end, _ = load_dc_period(info["start_year"])

        # check if an application already exists for this producer, this period and is not accepted
        identical_replacable_application = DoubleCountingApplication.objects.filter(
            Q(production_site_id=production_site.id)
            & Q(period_start__year=start.year)
            & Q(
                status__in=[
                    DoubleCountingApplication.PENDING,
                    DoubleCountingApplication.REJECTED,
                ]
            ),
        )

        if identical_replacable_application.exists():
            if should_replace:
                identical_replacable_application.delete()
            else:
                raise ValidationError({"message": DoubleCountingAddError.APPLICATION_ALREADY_EXISTS})

        # check if the agreement to link already exists
        if entity_type == Entity.ADMIN:
            if certificate_id_to_link:
                try:
                    agreement = DoubleCountingRegistration.objects.get(certificate_id=certificate_id_to_link)
                except Exception:
                    return Response(
                        {"message": DoubleCountingAddError.AGREEMENT_NOT_FOUND},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                try:
                    agreement = DoubleCountingRegistration.objects.get(
                        production_site=production_site,
                        valid_from=start,
                    )
                    return Response(
                        {"message": DoubleCountingAddError.AGREEMENT_ALREADY_EXISTS},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                except Exception:
                    agreement = None

        # create application
        dca, created = DoubleCountingApplication.objects.get_or_create(
            producer=producer,
            production_site_id=production_site.id,
            period_start=start,
            period_end=end,
            defaults={"producer_user": request.user},
        )

        if not created:
            raise ValidationError({"message": DoubleCountingAddError.APPLICATION_ALREADY_RECEIVED})

        if entity_type == Entity.ADMIN and certificate_id_to_link:
            dca.certificate_id = certificate_id_to_link
            dca.save()
            agreement.application = dca
            agreement.save()

        s3_path = f"doublecounting/{dca.id}_application_{dca.certificate_id}.xlsx"
        dca.download_link = default_storage.url(s3_path)
        dca.save()

        # 2 - save all production_data DoubleCountingProduction in db
        sourcing_forecast_data, _ = load_dc_sourcing_data(dca, sourcing_forecast_rows)
        production_data, _ = load_dc_production_data(
            dca, production_max_rows, production_forecast_rows, requested_quota_rows
        )
        production_history_data, _ = load_dc_production_history_data(
            dca, production_max_history_rows, production_effective_history_rows
        )
        sourcing_history_data, _ = load_dc_sourcing_history_data(dca, sourcing_history_rows)

        DoubleCountingSourcing.objects.filter(dca=dca).delete()
        for sourcing in sourcing_forecast_data:
            sourcing.save()

        DoubleCountingProduction.objects.filter(dca=dca).delete()
        for production in production_data:
            production.save()

        for sourcing_history in sourcing_history_data:
            sourcing_history.save()

        for production_history in production_history_data:
            production_history.save()

        # 3 - Upload file to S3
        try:
            default_storage.save(s3_path, file)
        except Exception:
            traceback.print_exc()

        # 4 - send emails
        try:
            send_dca_confirmation_email(dca, request)
        except Exception:
            print("email send error")
            traceback.print_exc()
        return Response({"status": "success"})
