from math import e

import requests
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.decorators import otp_or_403
from core.models import Entity
from entity.serializers import ResponseDataSerializer, SeachCompanySerializer


class SeachCompanyFormError:
    REGISTRATION_ID_ALREADY_USED = "REGISTRATION_ID_ALREADY_USED"
    NO_COMPANY_FOUND = "NO_COMPANY_FOUND"


@extend_schema(
    request=SeachCompanySerializer,
    responses=ResponseDataSerializer,
)
@api_view(["POST"])
@otp_or_403
def search_company_view(request):
    serializer = SeachCompanySerializer(data=request.data)  # Utiliser request.data avec DRF
    serializer.is_valid(raise_exception=True)

    registration_id = serializer.validated_data["registration_id"]
    try:
        company_found = search_company_gouv_fr(registration_id)
    except Exception:
        return Response(
            {"error": SeachCompanyFormError.NO_COMPANY_FOUND},
            status=status.HTTP_400_BAD_REQUEST,
        )

    company_siege = company_found["siege"]
    company_city = company_siege["libelle_commune"]
    company_zipcode = company_siege["code_postal"]
    company_address = company_siege["adresse"]
    string_to_remove = f"{company_zipcode} {company_city}"
    company_address = company_address.replace(string_to_remove, "")

    france = {
        "name": "France",
        "name_en": "France",
        "code_pays": "FR",
        "is_in_europe": True,
    }
    company_preview = {
        "name": company_found["nom_complet"],
        "legal_name": company_found["nom_raison_sociale"],
        "registration_id": company_found["siren"],
        "registered_address": company_address,
        "registered_city": company_siege["libelle_commune"],
        "registered_zipcode": company_siege["code_postal"],
        "registered_country": france,
    }

    response_data = {"company_preview": company_preview}
    try:
        entity = Entity.objects.get(registration_id=registration_id)
        response_data["warning"] = {
            "code": SeachCompanyFormError.REGISTRATION_ID_ALREADY_USED,
            "meta": {"company_name": entity.name},
        }
    except Entity.DoesNotExist:
        print("no registred company wit same siret")

    return Response(response_data, status=status.HTTP_200_OK)


def search_company_gouv_fr(siren):
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={siren}"
    api_response = requests.get(url)
    data = api_response.json()
    try:
        company = data["results"][0]
    except e:
        raise e
    return company
