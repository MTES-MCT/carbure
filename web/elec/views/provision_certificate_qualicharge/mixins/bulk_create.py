from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ProvisionCertificateBulkSerializer


class BulkCreateMixin:
    @extend_schema(
        operation_id="bulk_create_provision_certificates_qualicharge",
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

        all_double_validated_certificates = set(
            ElecProvisionCertificateQualicharge.objects.filter(
                validated_by=ElecProvisionCertificateQualicharge.BOTH
            ).values_list("station_id", "date_from", "date_to")
        )

        with transaction.atomic():
            for item in serializer.validated_data:
                siren = item["siren"]
                try:
                    cpo = Entity.objects.get(registration_id=siren)
                except Entity.DoesNotExist:
                    errors.append({"siren": siren, "error": "Entity not found"})
                    continue

                for unit in item["operational_units"]:
                    code = unit["code"]
                    stations = unit.get("stations", [])
                    for station in stations:
                        date_from = unit["from"]
                        date_to = unit["to"]
                        year = date_from.year
                        energy_amount = station["energy"]
                        station_id = station["id"]
                        is_controlled_by_qualicharge = station["is_controlled"]

                        if (station_id, date_from, date_to) in all_double_validated_certificates:
                            errors.append(
                                {
                                    "station_id": station_id,
                                    "error": "Provision certificate already validated and created",
                                }
                            )
                            continue

                        try:
                            cert, created = ElecProvisionCertificateQualicharge.objects.update_or_create(
                                station_id=station_id,
                                date_from=date_from,
                                date_to=date_to,
                                defaults={
                                    "cpo": cpo,
                                    "year": year,
                                    "operating_unit": code,
                                    "energy_amount": energy_amount,
                                    "is_controlled_by_qualicharge": is_controlled_by_qualicharge,
                                },
                            )

                        except Exception as e:
                            errors.append({"station_id": station_id, "error": str(e)})
                            continue

        return Response({"status": "success", "errors": errors}, status=status.HTTP_201_CREATED)
