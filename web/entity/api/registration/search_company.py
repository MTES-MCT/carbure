from math import e
from django import forms

from core.carburetypes import CarbureError
from core.decorators import check_user_rights, otp_or_403
from core.models import Pays, UserRights, Entity
from core.common import SuccessResponse, ErrorResponse
import requests


class SeachCompanyFormError:

    ENTITY_ = "ENTITY_CREATION_FAILED"
    REGISTRATION_ID_ALREADY_USED = "REGISTRATION_ID_ALREADY_USED"
    NO_COMPANY_FOUND = "NO_COMPANY_FOUND"


class SeachCompanyForm(forms.Form):
    registration_id = forms.CharField(max_length=9, required=True)  # SIREN


@otp_or_403
def search_company(request, *args, **kwargs):
    form = SeachCompanyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    registration_id = form.cleaned_data["registration_id"]
    try:
        company_found = search_company_gouv_fr(registration_id)
    except:
        return ErrorResponse(400, SeachCompanyFormError.NO_COMPANY_FOUND)

    company_siege = company_found["siege"]
    company_city = company_siege["libelle_commune"]
    company_zipcode = company_siege["code_postal"]
    company_address = company_siege["adresse"]
    string_to_remove = f"{company_zipcode} {company_city}"
    company_address = company_address.replace(string_to_remove, "")

    france = {"name": "France", "name_en": "France", "code_pays": "FR", "is_in_europe": True}
    company_preview = {
        "name": company_found["nom_complet"],
        "legal_name": company_found["nom_complet"],
        "registration_id": company_found["siren"],
        "registered_address": company_address,
        "registered_city": company_siege["libelle_commune"],
        "registered_zipcode": company_siege["code_postal"],
        "registered_country": france,
    }

    response = {"company_preview": company_preview}
    try:
        entity = Entity.objects.get(registration_id=registration_id)
        response["warning"] = {
            "code": SeachCompanyFormError.REGISTRATION_ID_ALREADY_USED,
            "meta": {"company_name": entity.name},
        }
        print("company_preview: ", company_preview)
    except:
        print("no registred company wit same siret")

    return SuccessResponse(response)


def search_company_gouv_fr(siren):
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={siren}"
    api_response = requests.get(url)
    data = api_response.json()
    try:
        company = data["results"][0]
    except e:
        raise e
    return company
