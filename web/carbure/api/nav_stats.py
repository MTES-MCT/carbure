from django.contrib.auth.models import User
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import (
    CarbureLot,
    Entity,
    ExternalAdminRights,
)
from doublecount.models import DoubleCountingApplication
from elec.models import ElecMeterReadingApplication
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.repositories.elec_audit_repository import ElecAuditRepository
from saf.models import SafTicket
from transactions.models import Depot, Site


class NavStatsSerializer(serializers.Serializer):
    total_pending_action_for_admin = serializers.IntegerField(required=False)
    pending_draft_lots = serializers.IntegerField(required=False)
    in_pending_lots = serializers.IntegerField(required=False)
    doublecount_agreement_pending = serializers.IntegerField(required=False)
    charge_point_registration_pending = serializers.IntegerField(required=False)
    metering_reading_pending = serializers.IntegerField(required=False)
    pending_transfer_certificates = serializers.IntegerField(required=False)
    audits = serializers.IntegerField(required=False)
    tickets = serializers.IntegerField(required=False)


def get_nav_stats(request):
    if not request or not request.user:
        return Response({})

    # @check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
    entity = request.entity
    if not entity:
        return Response({"error": "Entity ID is required"}, status=400)

    entity_id = entity.id
    response_data = {}

    if request.user == "ADMIN":
        pending_companies = Entity.objects.filter(status="PENDING").count()
        pending_users = User.objects.filter(status="PENDING").count()
        pending_certificates = ElecTransferCertificate.objects.filter(
            client_id=entity_id, status=ElecTransferCertificate.PENDING
        ).count()
        pending_sites = Site.objects.filter(status="PENDING").count()
        pending_depots = Depot.objects.filter(status="PENDING").count()
        total_pending_action_for_admin = (
            pending_companies + pending_users + pending_certificates + pending_sites + pending_depots
        )
        response_data["total_pending_action_for_admin"] = total_pending_action_for_admin

    if entity.entity_type != Entity.ADMIN:
        drafts = CarbureLot.objects.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
        in_pending = CarbureLot.objects.filter(carbure_client_id=entity_id, lot_status=CarbureLot.PENDING)
        response_data["pending_draft_lots"] = drafts.count()
        response_data["in_pending_lots"] = in_pending.count()

    if entity.entity_type in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]:
        doublecount_agreement_pending = DoubleCountingApplication.objects.filter(status=DoubleCountingApplication.PENDING)
        response_data["doublecount_agreement_pending"] = doublecount_agreement_pending.count()

        charge_point_registration_pending = ElecChargePointApplication.objects.filter(
            status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.AUDIT_DONE]
        )
        response_data["charge_point_registration_pending"] = charge_point_registration_pending.count()

        metering_reading_pending = ElecMeterReadingApplication.objects.filter(
            status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.AUDIT_DONE]
        )
        response_data["metering_reading_pending"] = metering_reading_pending.count()

    if entity.externaladminrights_set.filter(right=ExternalAdminRights.TRANSFERRED_ELEC).exists():
        pending_transfer_certificates = ElecTransferCertificate.objects.filter(status=ElecTransferCertificate.PENDING)
        response_data["pending_transfer_certificates"] = pending_transfer_certificates.count()
    elif entity.entity_type == Entity.OPERATOR and entity.has_elec:
        pending_transfer_certificates = ElecTransferCertificate.objects.filter(
            client_id=entity_id, status=ElecTransferCertificate.PENDING
        )
        response_data["pending_transfer_certificates"] = pending_transfer_certificates.count()

    if entity.entity_type == Entity.AUDITOR:
        audits = ElecAuditRepository.get_audited_applications(request.user).filter(status=ElecAuditSample.IN_PROGRESS)
        response_data["audits"] = audits.count()

    if entity.entity_type != Entity.ADMIN:
        tickets = SafTicket.objects.filter(status=SafTicket.PENDING, client_id=entity_id)
        response_data["tickets"] = tickets.count()

    serializer = NavStatsSerializer(response_data)
    return Response(serializer.data)


get_nav_stats = extend_schema(
    parameters=[
        OpenApiParameter("entity_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Entity ID", required=True),
    ],
    responses={"200": NavStatsSerializer},
)(api_view(["GET"])(get_nav_stats))
