from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from elec.models import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate_bulk import ProvisionCertificateBulkSerializer


class BulkCreateMixin:
    @extend_schema(
        operation_id="bulk_create_provision_certificates",
        description="Create multiple provision certificates in bulk (from Qualicharge)",
        request=ProvisionCertificateBulkSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "success", "errors": []}, description="Success message"),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-create",
    )
    def bulk_create(self, request, *args, **kwargs):
        serializer = ProvisionCertificateBulkSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        errors = []

        with transaction.atomic():
            for item in serializer.validated_data:
                siren = item["siren"]
                try:
                    cpo = Entity.objects.get(registration_id=siren)
                except Entity.DoesNotExist:
                    errors.append({"siren": siren, "error": "Entity not found"})
                    continue
                certs_to_create = []
                for unit in item["operational_units"]:
                    code = unit["code"]
                    stations = unit.get("stations", [])
                    energy_amount = sum(station["energy"] for station in stations) if stations else 0
                    from_date = unit["from"]
                    year = from_date.year
                    quarter = (from_date.month - 1) // 3 + 1
                    certs_to_create.append(
                        ElecProvisionCertificate(
                            cpo=cpo,
                            quarter=quarter,
                            year=year,
                            operating_unit=code,
                            source=ElecProvisionCertificate.QUALICHARGE,
                            energy_amount=energy_amount,
                            remaining_energy_amount=energy_amount,
                            compensation=False,
                        )
                    )
                try:
                    ElecProvisionCertificate.objects.bulk_create(certs_to_create)
                except Exception as e:
                    errors.append({"siren": siren, "error": str(e)})

        return Response({"status": "success", "errors": errors}, status=status.HTTP_201_CREATED)
