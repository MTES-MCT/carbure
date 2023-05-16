from core.models import CarbureLot, GenericError


def generic_error(error, **kwargs):
    d = {
        "display_to_creator": True,
        "display_to_admin": True,
        "display_to_auditor": True,
        "error": error,
    }
    d.update(kwargs)
    return GenericError(**d)


def is_french_delivery(lot: CarbureLot):
    return (
        lot.delivery_type
        in [
            CarbureLot.BLENDING,
            CarbureLot.TRADING,
            CarbureLot.STOCK,
            CarbureLot.DIRECT,
            CarbureLot.UNKNOWN,
        ]
        and lot.delivery_site_country
        and lot.delivery_site_country.code_pays == "FR"
    )


def enrich_lot(lot):
    queryset = CarbureLot.objects.filter(id=lot.id).select_related(
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
        "parent_stock",
        "parent_lot",
    )
    return queryset.first()
