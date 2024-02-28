from core.models import CarbureLot
from django.db.models.query_utils import Q


class TransactionsAdminLotsRepository:
    @staticmethod
    def get_admin_lots_by_status(entity, status, export=False):
        lots = CarbureLot.objects.select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_vendor",
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
        )
        if not export:
            lots = lots.prefetch_related("genericerror_set", "carbure_production_site__productionsitecertificate_set")

        lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])

        if status == "ALERTS":
            lots = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
                Q(highlighted_by_admin=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
            )
        elif status == "LOTS":
            lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])

        return lots
