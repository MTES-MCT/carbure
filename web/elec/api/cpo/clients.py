import traceback
from django import forms

from core.common import SuccessResponse, ErrorResponse
from core.models import Entity
from django.contrib.auth.decorators import login_required
from core.serializers import EntityPreviewSerializer


class ElecClientsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    CLIENT_LISTING_FAILED = "CLIENT_LISTING_FAILED"


class ElecClientsForm(forms.Form):
    q = forms.CharField(required=False)


@login_required
def get_clients(request, *args, **kwargs):
    clients_form = ElecClientsForm(request.GET)

    if not clients_form.is_valid():
        return ErrorResponse(400, ElecClientsError.MALFORMED_PARAMS, clients_form.errors)

    q = clients_form.cleaned_data["q"]

    entities = Entity.objects.filter(entity_type=Entity.OPERATOR, has_elec=True)
    if q:
        entities = entities.filter(name__icontains=q)

    try:
        serialized = EntityPreviewSerializer(entities, many=True)
        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecClientsError.CLIENT_LISTING_FAILED)
