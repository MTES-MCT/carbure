import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


def pretty_print_oldlot(tx):
    print(
        "OLD txid {id} (parent_tx_id {parent_tx_id}) lot_id {lot_id} (parent lot_id {parent_lot_id}) {carbure_id} {period} {dae} {feedstock} {biofuel} {volume} {delivery_date} [Supplier {supplier}] [Client {client}]".format(  # noqa: E501
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


def compare():
    lots_in_stock = CarbureLot.objects.filter(
        lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], delivery_type=CarbureLot.STOCK
    )
    for lot in lots_in_stock:
        try:
            stock = CarbureStock.objects.get(parent_lot=lot)
        except:
            try:
                child = CarbureLot.objects.get(parent_lot=lot, delivery_type=CarbureLot.STOCK)
                stock = CarbureStock.objects.get(parent_lot=child)
                if stock:
                    pretty_print_lot(lot)
                    pretty_print_lot(child)
                    lot.delivery_type = CarbureLot.TRADING
                    lot.save()
                    print("Parent should be TRADING - FIX")
            except:
                print("Could not find stock associated to this stock_lot")
    return

    # old_stocks = LotTransaction.objects.filter(is_stock=True, delivery_status__in=['A', 'F'])
    # for s in old_stocks:
    #     try:
    #         new_lot = CarbureLot.objects.get(transport_document_reference=s.dae, volume=s.lot.volume)
    #         if new_lot.lot_status == CarbureLot.REJECTED:
    #             continue
    #         new_stock = CarbureStock.objects.get(parent_lot__transport_document_reference=s.dae, parent_lot__volume=s.lot.volume)  # noqa: E501
    #         #pretty_print_oldlot(s)
    #         #pretty_print_stock(new_stock)
    #     except Exception as e:
    #         pretty_print_oldlot(s)
    #         print('Could not find new stock: %s' % (e))
    #         break


if __name__ == "__main__":
    compare()
