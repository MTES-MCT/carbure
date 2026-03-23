import requests
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from core.decorators import otp_or_403
from core.models import Entity
from entity.serializers import ResponseDataSerializer, SeachCompanySerializer

FRANCE = {
    "name": "France",
    "name_en": "France",
    "code_pays": "FR",
    "is_in_europe": True,
}

RECHERCHE_ENTREPRISES_URL = "https://recherche-entreprises.api.gouv.fr/search"


class SeachCompanyFormError:
    REGISTRATION_ID_ALREADY_USED = "REGISTRATION_ID_ALREADY_USED"
    NO_COMPANY_FOUND = "NO_COMPANY_FOUND"


class CompanyNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Company not found")
    default_code = "NO_COMPANY_FOUND"


@extend_schema(
    request=SeachCompanySerializer,
    responses=ResponseDataSerializer,
)
@api_view(["POST"])
@otp_or_403
def search_company_view(request):
    serializer = SeachCompanySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    registration_id = serializer.validated_data["registration_id"]

    company_preview = fetch_company_preview(registration_id)

    response_data = {"company_preview": company_preview}

    warning = build_registration_warning(registration_id)
    if warning:
        response_data["warning"] = warning

    return Response(response_data, status=status.HTTP_200_OK)


def fetch_company_preview(registration_id: str) -> dict:
    """Fetch company info from recherche-entreprises API and return a normalized preview."""
    is_siret = len(registration_id) == 14

    response = requests.get(RECHERCHE_ENTREPRISES_URL, params={"q": registration_id})
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        raise CompanyNotFoundError()

    company = results[0]
    etablissement = _get_etablissement(company, is_siret)

    return _build_preview(company, etablissement, is_siret)


def _get_etablissement(company: dict, is_siret: bool) -> dict:
    if is_siret:
        matching = company.get("matching_etablissements") or []
        if not matching:
            raise CompanyNotFoundError()
        return matching[0]
    return company["siege"]


def _build_preview(company: dict, etablissement: dict, is_siret: bool) -> dict:
    zipcode = etablissement.get("code_postal", "")
    city = etablissement.get("libelle_commune", "")
    address = etablissement.get("adresse", "")
    clean_address = address.replace(f"{zipcode} {city}", "").strip()

    if is_siret:
        department = get_department_from_postal_code(zipcode)
    else:
        department = etablissement.get("departement", "")

    return {
        "name": company.get("nom_complet", ""),
        "legal_name": company.get("nom_raison_sociale", ""),
        "registration_id": company.get("siren", ""),
        "registered_address": clean_address,
        "registered_city": city,
        "registered_zipcode": zipcode,
        "registered_country": FRANCE,
        "department_code": department,
        "insee_code": etablissement.get("commune", ""),
    }


def build_registration_warning(registration_id: str) -> dict | None:
    entity = Entity.objects.filter(registration_id=registration_id).order_by("date_added").first()
    if not entity:
        return None

    warning = {
        "code": SeachCompanyFormError.REGISTRATION_ID_ALREADY_USED,
        "meta": {"company_name": entity.name},
    }

    biomethane_entities = Entity.objects.filter(
        registration_id=registration_id,
        entity_type=Entity.BIOMETHANE_PRODUCER,
    ).order_by("date_added")

    if biomethane_entities.exists():
        warning["meta"]["entities"] = [{"name": e.name, "entity_type": e.entity_type} for e in biomethane_entities]

    return warning


def get_department_from_postal_code(postal_code: str) -> str:
    if postal_code.startswith("97"):
        return postal_code[:3]
    if postal_code.startswith("20"):
        return "2A" if postal_code < "20200" else "2B"
    return postal_code[:2]
