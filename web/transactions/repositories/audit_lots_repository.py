from django.db.models.query_utils import Q
from core.models import CarbureLot, CarbureLotComment, UserRights
from core.serializers import CarbureLotCommentSerializer


class TransactionsAuditLotsRepository:
    @staticmethod
    def get_auditor_lots(request):
        rights = request.session.get("rights")
        allowed_entities = [entity for entity in rights if rights[entity] == UserRights.AUDITOR]

        lots = CarbureLot.objects.select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_production_site",
            "carbure_production_site__producer",
            "carbure_production_site__country",
            "production_country",
            "carbure_dispatch_site",
            "carbure_dispatch_site__country",
            "dispatch_site_country",
            "carbure_delivery_site",
            "carbure_delivery_site__country",
            "delivery_site_country",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "parent_lot",
            "parent_stock",
            "parent_stock__carbure_client",
            "parent_stock__carbure_supplier",
            "parent_stock__feedstock",
            "parent_stock__biofuel",
            "parent_stock__depot",
            "parent_stock__country_of_origin",
            "parent_stock__production_country",
        ).prefetch_related("genericerror_set", "carbure_production_site__productionsitecertificate_set")

        lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        return lots.filter(
            Q(carbure_client__in=allowed_entities)
            | Q(carbure_supplier__in=allowed_entities)
            | Q(added_by__in=allowed_entities)
        )

    @staticmethod
    def get_auditor_lots_by_status(entity, status, request):
        lots = TransactionsAuditLotsRepository.get_auditor_lots(request)
        if status == "ALERTS":
            lots = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
                Q(highlighted_by_auditor=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
            )
        elif status == "LOTS":
            lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        return lots

    @staticmethod
    def get_auditor_lot_comments(lot):
        if lot is None:
            return []
        comments = lot.carburelotcomment_set.filter(
            Q(comment_type=CarbureLotComment.AUDITOR) | Q(is_visible_by_auditor=True)
        )
        return CarbureLotCommentSerializer(comments, many=True).data

    @staticmethod
    def get_audited_entities(user):
        rights = UserRights.objects.filter(user=user, role=UserRights.AUDITOR)
        return rights.values_list("entity", flat=True)
