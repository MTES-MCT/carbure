import datetime
from core.carburetypes import CarbureSanityCheckErrors
from core.common import find_normalized
from core.models import CarbureLot
from .helpers import generic_error


def check_volume_faible(lot: CarbureLot):
    if lot.volume < 2000 and lot.delivery_type not in [
        CarbureLot.RFC,
        CarbureLot.FLUSHED,
    ]:
        return generic_error(
            error=CarbureSanityCheckErrors.VOLUME_FAIBLE,
            lot=lot,
            field="volume",
        )


def check_locked_year(lot: CarbureLot, prefetched_data):
    if lot.year in prefetched_data["locked_years"] or lot.year <= 2015:
        generic_error(
            error=CarbureSanityCheckErrors.YEAR_LOCKED,
            lot=lot,
            field="delivery_date",
            extra=str(lot.year),
            is_blocking=True,
        )


def check_delivery_in_the_future(lot: CarbureLot):
    in_two_weeks = datetime.date.today() + datetime.timedelta(days=15)

    if lot.delivery_date and lot.delivery_date > in_two_weeks:
        return generic_error(
            error=CarbureSanityCheckErrors.DELIVERY_IN_THE_FUTURE,
            lot=lot,
            extra="La date de livraison est dans le futur",
            value=lot.delivery_date,
            field="delivery_date",
            is_blocking=True,
        )


def check_mac_bc_wrong(lot: CarbureLot):
    mac_biofuels = ("ED95", "B100", "ETH", "EMHV", "EMHU")
    if lot.delivery_type == CarbureLot.RFC and lot.biofuel and lot.biofuel.code not in mac_biofuels:
        return generic_error(
            error=CarbureSanityCheckErrors.MAC_BC_WRONG,
            lot=lot,
            is_blocking=True,
            fields=["biofuel", "delivery_type"],
        )


def check_mac_not_efpe(lot: CarbureLot):
    if (
        lot.delivery_type == CarbureLot.RFC
        and lot.carbure_delivery_site
        and lot.carbure_delivery_site.depot_type != "EFPE"
    ):
        return generic_error(
            error=CarbureSanityCheckErrors.MAC_NOT_EFPE,
            lot=lot,
            fields=["delivery_type"],
        )


def check_mp_not_configured(lot: CarbureLot, prefetched_data):
    if lot.feedstock and lot.carbure_production_site:
        production_site = find_normalized(lot.carbure_production_site.name, prefetched_data["my_production_sites"])
        if production_site:
            mps = [psi.matiere_premiere for psi in production_site.productionsiteinput_set.all()]
            if lot.feedstock not in mps:
                return generic_error(
                    error=CarbureSanityCheckErrors.MP_NOT_CONFIGURED,
                    lot=lot,
                    display_to_recipient=False,
                    field="feedstock_code",
                )


def check_bc_not_configured(lot: CarbureLot, prefetched_data):
    if lot.biofuel and lot.carbure_production_site:
        production_site = find_normalized(lot.carbure_production_site.name, prefetched_data["my_production_sites"])
        if production_site:
            bcs = [pso.biocarburant for pso in production_site.productionsiteoutput_set.all()]
            if lot.biofuel not in bcs:
                return generic_error(
                    error=CarbureSanityCheckErrors.BC_NOT_CONFIGURED,
                    lot=lot,
                    display_to_recipient=False,
                    field="biofuel_code",
                )


def check_depot_not_configured(lot: CarbureLot, prefetched_data):
    if lot.carbure_client and lot.delivery_type != CarbureLot.TRADING:  # ignore delivery issues for trading
        depots_by_entity = prefetched_data["depotsbyentity"]
        depots = depots_by_entity.get(lot.carbure_client.pk, [])

        if lot.carbure_delivery_site is not None and lot.carbure_delivery_site.depot_id not in depots:
            # not a single delivery sites linked to entity
            return generic_error(
                error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED,
                lot=lot,
                display_to_recipient=True,
                display_to_creator=False,
                field="delivery_site",
            )
