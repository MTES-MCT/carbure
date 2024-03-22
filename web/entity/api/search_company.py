from math import e
from django import forms

from core.carburetypes import CarbureError
from core.decorators import check_user_rights, otp_or_403
from core.models import UserRights, Entity
from core.common import SuccessResponse, ErrorResponse
import requests


class SeachCompanyFormError:

    ENTITY_ = "ENTITY_CREATION_FAILED"
    REGISTRATION_ID_FORMAT_INVALID = "REGISTRATION_ID_FORMAT_INVALID"
    NO_COMPANY_FOUND = "NO_COMPANY_FOUND"


class SeachCompanyForm(forms.Form):
    registration_id = forms.CharField(max_length=9, required=True)  # SIREN


# @otp_or_403
def search_company(request, *args, **kwargs):
    form = SeachCompanyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    registration_id = form.cleaned_data["registration_id"]
    print("registration_id: ", registration_id)

    # url = f"https://recherche-entreprises.api.gouv.fr/search?q={registration_id}"
    # api_response = requests.get(url)
    # data = api_response.json()
    # try:
    #     company_found = data["results"][0]
    # except:
    #     return ErrorResponse(400, SeachCompanyFormError.NO_COMPANY_FOUND)

    # company_siege = company_found["siege"]
    # company_city = company_siege["libelle_commune"]
    # company_zipcode = company_siege["code_postal"]
    # company_address = company_siege["adresse"]
    # string_to_remove = f"{company_zipcode} {company_city}"
    # company_address = company_address.replace(string_to_remove, "")

    # company_preview = {
    #     "name": company_found["nom_complet"],
    #     "legal_name": company_found["nom_complet"],
    #     "registration_id": company_found["siren"],
    #     "registered_address": company_address,
    #     "registered_city": company_siege["libelle_commune"],
    #     "registered_zipcode": company_siege["code_postal"],
    #     "registered_country": "France",
    # }
    # print("company_preview: ", company_preview)

    # check if not already exists
    # try:
    #     entity = Entity.objects.get(registration_id=registration_id)
    # except:

    company_preview = {
        "name": "TOTALENERGIES SE",
        "legal_name": "TOTALENERGIES SE",
        "registration_id": "542051180",
        "registered_address": "LA DEFENSE 6 2 PL JEAN MILLIER ",
        "registered_city": "COURBEVOIE",
        "registered_zipcode": "92400",
        "registered_country": "France",
    }
    return SuccessResponse(company_preview)
