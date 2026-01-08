from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from core.models import CarbureNotification
from elec.models import ElecTransferCertificate


class CancelActionMixin:
    @extend_schema(request=None, responses=None)
    @action(methods=["POST"], detail=True)
    @transaction.atomic
    def cancel(self, request, id=None):
        transfer_certificate = self.get_object()

        if transfer_certificate.status == ElecTransferCertificate.ACCEPTED:
            raise ParseError("ALREADY_ACCEPTED")

        transfer_certificate.delete()
        CarbureNotification.objects.filter(meta__transfer_certificate_id=transfer_certificate.id).delete()
        return Response()
