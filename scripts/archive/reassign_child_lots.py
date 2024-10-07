import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


def pretty_print_oldlot(tx):
    print(
        "OLD txid {id} (parent_tx_id {parent_tx_id}) lot_id {lot_id} (parent lot_id {parent_lot_id}) {carbure_id} {period} {dae} {feedstock} {biofuel} {volume} {delivery_date} Supplier {supplier} Client {client}".format(  # noqa: E501
            id=tx.id,
            parent_tx_id=tx.parent_tx.id if tx.parent_tx else None,
            lot_id=tx.lot.id,
            parent_lot_id=tx.lot.parent_lot.id if tx.lot.parent_lot else None,
            carbure_id=tx.lot.carbure_id,
            period=tx.lot.period,
            dae=tx.dae,
            biofuel=tx.lot.biocarburant.name,
            feedstock=tx.lot.matiere_premiere.name,
            volume=tx.lot.volume,
            delivery_date=tx.delivery_date,
            supplier=tx.carbure_vendor.name if tx.carbure_vendor else "UNKNOWN",
            client=tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
        )
    )


def pretty_print_lot(lot):
    print(
        "NEW [added by {added_by}] id {id} (parent lot {parent_lot}) (parent_stock {parent_stock}) {carbure_id} {period} {dae} {feedstock} {biofuel} {volume} {delivery_date} {delivery_type} {status} Supplier {supplier} Client {client}".format(  # noqa: E501
            added_by=lot.added_by.name,
            id=lot.id,
            parent_lot=lot.parent_lot.id if lot.parent_lot else None,
            parent_stock=lot.parent_stock.id if lot.parent_stock else None,
            carbure_id=lot.carbure_id,
            period=lot.period,
            dae=lot.transport_document_reference,
            biofuel=lot.biofuel.name,
            feedstock=lot.feedstock.name,
            volume=lot.volume,
            delivery_date=lot.delivery_date,
            delivery_type=lot.delivery_type,
            status=lot.lot_status,
            supplier=lot.carbure_supplier.name if lot.carbure_supplier else lot.unknown_supplier,
            client=lot.carbure_client.name if lot.carbure_client else lot.unknown_client,
        )
    )


def pretty_print_stock(stock):
    print(
        "{id} {carbure_id} {initial_volume} remaining {remaining_volume} {biofuel} {feedstock}".format(
            id=stock.id,
            carbure_id=stock.carbure_id,
            initial_volume=stock.parent_lot.volume if stock.parent_lot else 0,
            remaining_volume=stock.remaining_volume,
            biofuel=stock.biofuel.name,
            feedstock=stock.feedstock.name,
        )
    )


def handle_lot(lot):
    pretty_print_lot(lot)
    old_tx = LotTransaction.objects.get(
        dae=lot.transport_document_reference, lot__volume=lot.volume, carbure_client=lot.carbure_client
    )
    pretty_print_oldlot(old_tx)
    if old_tx.parent_tx is None:
        print("NO PARENT TX .. ODD")
        input("go to next")
        return
    pretty_print_oldlot(old_tx.parent_tx)
    theo_parent_lot = CarbureLot.objects.get(
        volume=old_tx.parent_tx.lot.volume,
        transport_document_reference=old_tx.parent_tx.dae,
        carbure_client=lot.carbure_supplier,
    )
    pretty_print_lot(theo_parent_lot)
    try:
        # is the lot coming from a stock ?
        stock = CarbureStock.objects.get(parent_lot=theo_parent_lot)
        print("THEO LINKED STOCK")
        pretty_print_stock(stock)
        stock.remaining_volume = round(stock.remaining_volume - lot.volume, 2)
        stock.remaining_weight = stock.get_weight()
        stock.remaining_lhv_amount = stock.get_lhv_amount()
        stock.save()
        lot.parent_stock = stock
        lot.save()
    except:
        # could not find stock. is it a TRADING Lot ?
        print("Could not find linked stock")

        res = input("Enter new parent lot_id:")
        try:
            tid = int(res)
        except:
            return
        candidate = CarbureLot.objects.get(id=tid)
        if candidate.lot_status not in (CarbureLot.ACCEPTED, CarbureLot.FROZEN):
            candidate.lot_status = CarbureLot.ACCEPTED
        if candidate.delivery_type == CarbureLot.UNKNOWN:
            candidate.delivery_type = CarbureLot.TRADING
        # candidate.save()
        lot.parent_lot_id = tid
        # lot.save()


def reassign():
    odd_lots = CarbureLot.objects.filter(
        carbure_producer__isnull=False,
        parent_lot__isnull=True,
        parent_stock__isnull=True,
        carbure_supplier__entity_type=Entity.TRADER,
    )
    for lot in odd_lots:
        if lot.carbure_producer == lot.carbure_supplier:
            continue
        print("##################################################")
        handle_lot(lot)


if __name__ == "__main__":
    reassign()
