from django.contrib.auth.models import User
from django.http.response import JsonResponse
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import (
    ListModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from core.models import (
    CarbureLot,
    Entity,
)
from doublecount.models import DoubleCountingApplication
from elec.models import ElecMeterReadingApplication
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.repositories.elec_audit_repository import ElecAuditRepository
from saf.models import SafTicket
from transactions.models import Depot, Site


class NavStatsViewSet(ListModelMixin, GenericViewSet):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        responses={"200": dict},
    )
    def list(self, request, *args, **kwargs):
        # @check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
        entity_id = request.GET["entity_id"]
        entity = Entity.objects.get(id=entity_id)
        response = {}

        if request.user == "ADMIN":
            # Admin (uniquement pour les comptes admin)
            # somme du nombre d'actions en attente pour un admin (Nombre de sociétés et d'utilisateurs à autoriser
            # + nombre de certificats à valider + Sites de production et Dépôts à valider)
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
            response["total_pending_action_for_admin"] = total_pending_action_for_admin

        if entity.entity_type != Entity.ADMIN:
            # Biocarburants (endpoint actuel /transactions/snapshot) NON ADMIN
            #       Nombre de lots brouillons EN ATTENTE
            #       Nombre de lots reçus EN ATTENTE
            drafts = CarbureLot.objects.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
            in_pending = CarbureLot.objects.filter(carbure_client_id=entity_id, lot_status=CarbureLot.PENDING)
            response["pending_draft_lots"] = drafts.count()
            response["in_pending_lots"] = in_pending.count()

        if entity.entity_type in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]:
            # Double comptage (uniquement pour les comptes admin + EXTERNAL ADMIN DOUBLE COMPTAGE)
            #   Nombre de demandes d'agréments en attente
            doublecount_agreement_pending = DoubleCountingApplication.objects.filter(
                status=DoubleCountingApplication.PENDING
            )
            response["doublecount_agreement_pending"] = doublecount_agreement_pending.count()

            # Nombre d'inscriptions de PDC en attente (somme des dossiers de PDC qui ont le status
            # EN ATTENTE ou AUDIT A VALIDER) (uniquement pour les types d'entité Administration
            # OU qui ont les droits externes elec)
            charge_point_registration_pending = ElecChargePointApplication.objects.filter(
                status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.AUDIT_IN_PROGRESS]
            )
            response["charge_point_registration_pending"] = charge_point_registration_pending.count()

            # Nombre de déclarations de relevés en attente (somme des déclarations de relevés qui ont
            # le status EN ATTENTE ou AUDIT A VALIDER)
            # (uniquement pour les types d'entité Administration OU qui ont les droits externes elec)
            metering_reading_pending = ElecMeterReadingApplication.objects.filter(
                status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.AUDIT_IN_PROGRESS]
            )
            response["metering_reading_pending"] = metering_reading_pending.count()

        if entity.entity_type == Entity.OPERATOR and entity.has_elec:
            # Certificats d'elec
            # Nombre de certificats en attente (endpoint actuel elec/operator/snapshot) UNIQUEMENT POUR OPERATEURS qui
            # acceptent des volumes d'electricité entitytype === "operator" ET entity.has_elec = true
            pending_transfer_certificates = ElecTransferCertificate.objects.filter(
                client_id=entity_id, status=ElecTransferCertificate.PENDING
            )
            response["pending_transfer_certificates"] = pending_transfer_certificates.count()

        if entity.entity_type == Entity.AUDITOR:
            # Nombre de points de recharge à auditer (endpoint elec/auditor/snapshot) (UNIQUEMENT POUR AUDITEUR)
            audits = ElecAuditRepository.get_audited_applications(request.user).filter(status=ElecAuditSample.IN_PROGRESS)
            response["audits"] = audits.count()

        if entity.entity_type != Entity.ADMIN:  # and request.user.saf_management TODO
            # SAF (uniquement comptes non admin qui gèrent du saf)
            # Nombre de tickets reçus en attente
            tickets = SafTicket.objects.filter(status=SafTicket.PENDING)
            response["tickets"] = tickets.count()

        return JsonResponse(response)
