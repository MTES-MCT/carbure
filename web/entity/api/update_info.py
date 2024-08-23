from django import forms

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, Pays, UserRights


class UpdateEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ENTITY_CREATION_FAILED = "ENTITY_CREATION_FAILED"
    REGISTRATION_ID_FORMAT_INVALID = "REGISTRATION_ID_FORMAT_INVALID"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_entity_info(request, *args, **kwargs):
    form = UpdateEntityInfoForm(request.POST)
    if not form.is_valid():
        return ErrorResponse(400, UpdateEntityError.MALFORMED_PARAMS, form.errors)

    entity_id = kwargs["context"]["entity_id"]

    legal_name = form.cleaned_data["legal_name"]
    registration_id = form.cleaned_data["registration_id"]
    sustainability_officer_phone_number = form.cleaned_data["sustainability_officer_phone_number"]
    sustainability_officer_email = form.cleaned_data["sustainability_officer_email"]
    sustainability_officer = form.cleaned_data["sustainability_officer"]
    registered_address = form.cleaned_data["registered_address"]
    registered_zipcode = form.cleaned_data["registered_zipcode"]
    registered_city = form.cleaned_data["registered_city"]
    registered_country = form.cleaned_data["registered_country_code"]
    activity_description = form.cleaned_data["activity_description"]
    website = form.cleaned_data["website"]
    vat_number = form.cleaned_data["vat_number"]

    entity = Entity.objects.get(id=entity_id)
    entity.legal_name = legal_name
    entity.sustainability_officer_phone_number = sustainability_officer_phone_number
    entity.registration_id = registration_id
    entity.sustainability_officer = sustainability_officer
    entity.sustainability_officer_email = sustainability_officer_email
    entity.registered_address = registered_address
    entity.registered_zipcode = registered_zipcode
    entity.registered_city = registered_city
    entity.registered_country = registered_country
    entity.activity_description = activity_description
    entity.website = website
    entity.vat_number = vat_number
    entity.save()
    return SuccessResponse()


class UpdateEntityInfoForm(forms.Form):
    activity_description = forms.CharField(max_length=5000, required=False)
    entity_id = forms.IntegerField()
    legal_name = forms.CharField(max_length=128, required=False)
    registered_address = forms.CharField(required=False)
    registered_city = forms.CharField(required=False)
    registered_country_code = forms.ModelChoiceField(queryset=Pays.objects.all(), to_field_name="code_pays", required=False)
    registered_zipcode = forms.CharField(required=False)
    registration_id = forms.CharField(max_length=64, required=False)
    sustainability_officer = forms.CharField(max_length=256, required=False)
    sustainability_officer_email = forms.CharField(max_length=254, required=False)
    sustainability_officer_phone_number = forms.CharField(max_length=32, required=False)
    vat_number = forms.CharField(max_length=32, required=False)
    website = forms.URLField(required=False)
