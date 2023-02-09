from django.urls import path, include
import traceback

from core.decorators import check_user_rights
from core.models import UserRights, Entity, ExternalAdminRights
from core.common import SuccessResponse, ErrorResponse

class UpdateEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ENTITY_CREATION_FAILED = "ENTITY_CREATION_FAILED"

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_entity(request, *args, **kwargs):
    entity_id = kwargs['context']['entity_id']
    legal_name = request.POST.get('legal_name', '')
    registration_id = request.POST.get('registration_id', '')
    sustainability_officer_phone_number = request.POST.get('sustainability_officer_phone_number', '')
    sustainability_officer = request.POST.get('sustainability_officer', '')
    registered_address = request.POST.get('registered_address', '')
    registered_zipcode = request.POST.get('registered_zipcode', '')
    registered_city = request.POST.get('registered_city', '')
    registered_country = request.POST.get('registered_country', '')

    entity = Entity.objects.get(id=entity_id)
    entity.legal_name = legal_name
    entity.sustainability_officer_phone_number = sustainability_officer_phone_number
    entity.registration_id = registration_id
    entity.sustainability_officer = sustainability_officer
    entity.registered_address = registered_address
    entity.registered_zipcode = registered_zipcode
    entity.registered_city = registered_city
    entity.registered_country = registered_country
    entity.save()
    return SuccessResponse()