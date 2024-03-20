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


class SeachCompanyForm(forms.Form):
    entity_id = forms.IntegerField()
    registration_id = forms.CharField(max_length=64, required=False)  # SIREN


# @otp_or_403
def search_company(request, *args, **kwargs):
    print("OK")
    form = SeachCompanyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    registration_id = form.cleaned_data["registration_id"]
    print("registration_id: ", registration_id)

    url = "https://recherche-entreprises.api.gouv.fr/search"
    params = {"q": registration_id}
    api_response = requests.get(url, params)
    print("api_response: ", api_response)

    # check if not already exists
    # try:
    #     entity = Entity.objects.get(registration_id=registration_id)
    # except:

    return SuccessResponse({"data": api_response})
