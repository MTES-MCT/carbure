from datetime import datetime

from django.db import transaction
from django.db.models.query_utils import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationSerializer
from doublecount.errors import DoubleCountingError

from .utils import add_quotas_to_agreements


class AgreementListsSerializer(serializers.Serializer):
    active = DoubleCountingRegistrationSerializer(many=True)
    incoming = DoubleCountingRegistrationSerializer(many=True)
    expired = DoubleCountingRegistrationSerializer(many=True)
    inactive = DoubleCountingRegistrationSerializer(many=True)


class AgreementStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=DoubleCountingRegistration.STATUS_CHOICES)


class AgreementStatusBulkUpdateSerializer(AgreementStatusUpdateSerializer):
    agreement_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, max_length=100)
    status = serializers.ChoiceField(
        choices=[
            DoubleCountingRegistration.SUSPENDED,
            DoubleCountingRegistration.WITHDRAWN,
            DoubleCountingRegistration.TERMINATED,
        ]
    )


class AgreementAdminListActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=AgreementStatusBulkUpdateSerializer,
        responses={
            200: inline_serializer(
                name="AgreementStatusBulkUpdateResponse",
                fields={"updated_count": serializers.IntegerField()},
            ),
            400: inline_serializer(
                name="AgreementStatusBulkUpdateErrorResponse",
                fields={"message": serializers.CharField()},
            ),
        },
    )
    @action(methods=["post"], detail=False, url_path="bulk-update-status")
    def bulk_update_status(self, request, *args, **kwargs):
        serializer = AgreementStatusBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agreement_ids = set(serializer.validated_data["agreement_ids"])
        with transaction.atomic():
            agreements = list(
                self.get_queryset()
                .select_related(None)
                .filter(id__in=agreement_ids, status=DoubleCountingRegistration.VALID)
                .select_for_update()
            )
            if {agreement.id for agreement in agreements} != agreement_ids:
                raise ValidationError({"message": DoubleCountingError.AGREEMENTS_NOT_UPDATABLE})

            for agreement in agreements:
                agreement.status = serializer.validated_data["status"]
            DoubleCountingRegistration.objects.bulk_update(agreements, ["status"])

        return Response({"updated_count": len(agreement_ids)})

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=AgreementStatusUpdateSerializer,
        responses={200: AgreementStatusUpdateSerializer},
    )
    @action(methods=["patch"], detail=True, url_path="update-status")
    def update_status(self, request, *args, **kwargs):
        serializer = AgreementStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agreement = self.get_object()
        agreement.status = serializer.validated_data["status"]
        agreement.save(update_fields=["status"])
        return Response({"status": agreement.status})

    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(
                "year",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Year",
                required=False,
            ),
        ],
        responses=AgreementListsSerializer,
    )
    @action(methods=["get"], detail=False, url_path="agreement-admin")
    def agreement_admin(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        year = self.request.query_params.get("year", datetime.now().year)

        agreements_active = queryset.filter(
            Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year),
            status=DoubleCountingRegistration.VALID,
        )

        agreements_incoming = queryset.filter(Q(valid_from__year__gt=year), status=DoubleCountingRegistration.VALID)
        agreements_expired = queryset.filter(Q(valid_until__year__lt=year), status=DoubleCountingRegistration.VALID)
        agreements_inactive = queryset.exclude(status=DoubleCountingRegistration.VALID)

        active_agreements = DoubleCountingRegistrationSerializer(agreements_active, many=True).data
        active_agreements_with_quotas = add_quotas_to_agreements(year, active_agreements)

        data = {
            "active": active_agreements_with_quotas,
            "incoming": DoubleCountingRegistrationSerializer(agreements_incoming, many=True).data,
            "expired": DoubleCountingRegistrationSerializer(agreements_expired, many=True).data,
            "inactive": DoubleCountingRegistrationSerializer(agreements_inactive, many=True).data,
        }
        return Response(data)
