import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *


def fix_missing_stocks():
    lots_wo_carbureid = CarbureLot.objects.filter(lot_status__in=[CarbureLot.FROZEN, CarbureLot.ACCEPTED], carbure_id="")
    for lot in lots_wo_carbureid:
        print("Generate carbureid for lot %d" % (lot.id))
        lot.generate_carbure_id()
        lot.save()

    stocks_wo_carbureid = CarbureStock.objects.filter(carbure_id="")
    for stock in stocks_wo_carbureid:
        print("Generate carbureid for stock %d" % (stock.id))
        stock.generate_carbure_id()
        stock.save()

    should_be_stock = CarbureLot.objects.filter(
        carbure_client_id=93, delivery_type=CarbureLot.BLENDING, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN]
    )
    for lot in should_be_stock:
        print("Should be stock %d" % (lot.id))
        stock = CarbureStock()
        stock.parent_lot = lot
        if lot.carbure_delivery_site is None:
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
            return JsonResponse({"status": "error", "message": "Cannot add stock for unknown Depot"}, status=400)
        stock.depot = lot.carbure_delivery_site
        stock.carbure_client = lot.carbure_client
        stock.remaining_volume = lot.volume
        stock.remaining_weight = lot.weight
        stock.remaining_lhv_amount = lot.lhv_amount
        stock.feedstock = lot.feedstock
        stock.biofuel = lot.biofuel
        stock.country_of_origin = lot.country_of_origin
        stock.carbure_production_site = lot.carbure_production_site
        stock.unknown_production_site = lot.unknown_production_site
        stock.production_country = lot.production_country
        stock.carbure_supplier = lot.carbure_supplier
        stock.unknown_supplier = lot.unknown_supplier
        stock.ghg_reduction = lot.ghg_reduction
        stock.ghg_reduction_red_ii = lot.ghg_reduction_red_ii
        stock.save()
        stock.carbure_id = "%sS%d" % (lot.carbure_id, stock.id)
        stock.save()
        lot.delivery_type = CarbureLot.STOCK
        lot.save()


if __name__ == "__main__":
    fix_missing_stocks()
