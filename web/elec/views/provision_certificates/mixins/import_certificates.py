import pandas as pd
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from core.utils import normalize_string
from elec.models import ElecProvisionCertificate


class ImportActionMixin:
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
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary", "description": "CSV file to import"}},
                "required": ["file"],
            }
        },
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={},
                request_only=False,
                response_only=True,
            ),
        ],
        responses={200: {"type": "object", "properties": {}}},
    )
    @action(methods=["POST"], detail=False, url_path="import")
    def import_certificates(self, request):
        file = request.FILES.get("file")
        if file is None:
            raise Exception("MISSING_FILE")

        certificate_df = pd.read_csv(file, sep=";", decimal=",")

        print(certificate_df)

        cpos = Entity.objects.filter(entity_type=Entity.CPO)
        cpos_by_name = {normalize_string(cpo.name): cpo for cpo in cpos}

        missing_cpos = []
        for certificate in certificate_df.to_dict("records"):
            if normalize_string(certificate["cpo"]) not in cpos_by_name:
                missing_cpos.append(certificate["cpo"])

        if len(missing_cpos) > 0:
            raise Exception("MISSING_CPO")

        certificate_model_instances = []
        for record in certificate_df.to_dict("records"):
            certif = ElecProvisionCertificate(
                cpo=cpos_by_name.get(normalize_string(record["cpo"])),
                quarter=record["quarter"],
                year=record["year"],
                operating_unit=record["operating_unit"],
                energy_amount=record["energy_amount"],
                source=ElecProvisionCertificate.MANUAL,
                remaining_energy_amount=record["energy_amount"],
            )
            certificate_model_instances.append(certif)

        ElecProvisionCertificate.objects.bulk_create(certificate_model_instances)

        return Response()
