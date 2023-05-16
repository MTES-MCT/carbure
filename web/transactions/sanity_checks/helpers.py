import datetime
from core.models import CarbureLot, GenericError

july1st2021 = datetime.date(year=2021, month=7, day=1)


# quickly create a lot error
def generic_error(error, **kwargs):
    d = {
        "display_to_creator": True,
        "display_to_admin": True,
        "display_to_auditor": True,
        "error": error,
    }
    d.update(kwargs)
    return GenericError(**d)


# check if the lot is bound to RED II rules
def is_red_ii(lot: CarbureLot):
    if not lot.delivery_date:
        return True
    return lot.delivery_date >= july1st2021


# check if the lot is a delivery to france
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


# check if the given error is found in the list
def has_error(error, error_list):
    for e in error_list:
        if e.error == error:
            return True
    return False


# select data related to a lot to speed up sanity checks
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
    return queryset.get()
