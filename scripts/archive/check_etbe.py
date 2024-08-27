import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402

if __name__ == "__main__":
    # Link Lot -> Parent Lot but not Tx -> Parent Tx
    # get all tx with parent_tx is None but lot.parent_lot is not None
    etbe_child = LotTransaction.objects.filter(
        lot__parent_lot__isnull=False, lot__biocarburant__code="ETBE", lot__parent_lot__biocarburant__code="ETH"
    )
    for e in etbe_child:
        if e.parent_tx is None:
            potential_parent = LotTransaction.objects.filter(lot_id=e.lot.parent_lot_id)
            if potential_parent.count() == 1:
                print("Linking child ETBE %s transaction with ETH parent %s" % (e.id, potential_parent[0].id))
                e.parent_tx = potential_parent[0]
                e.save()

    # mark all ETH lots with ETBE child as 'transformed'
    etbe_child = LotTransaction.objects.filter(lot__biocarburant__code="ETBE", lot__parent_lot__biocarburant__code="ETH")
    for e in etbe_child:
        if not e.lot.parent_lot.is_transformed:
            print("parent tx %d lot %d not flagged as transformed, do it" % (e.parent_tx_id, e.parent_tx.lot.id))
            e.lot.parent_lot.is_transformed = True
            e.lot.parent_lot.save()

    # check that all transformations have a link (new_stock.parent_tx == previous_stock)
    transformations = ETBETransformation.objects.all()
    for t in transformations:
        if t.new_stock.parent_tx_id != t.previous_stock_id:
            print("link transformation txs together prev %d new %d" % (t.previous_stock.id, t.new_stock.id))
            t.new_stock.parent_tx = t.previous_stock
            t.new_stock.save()

    transformed_in = [e.previous_stock_id for e in transformations]
    transformed_out = [e.new_stock_id for e in transformations]
    # missing transformations
    etbe_child = LotTransaction.objects.filter(
        lot__biocarburant__code="ETBE", lot__parent_lot__biocarburant__code="ETH"
    ).exclude(parent_tx__is_forwarded=True)
    for e in etbe_child:
        if e.id not in transformed_out:
            print(
                "Found linked ETH-ETBE lots/transactions with no transformation. %s Parent lot %s Tx %s Parent Tx %s"
                % (e.lot.id, e.lot.parent_lot_id, e.id, e.parent_tx_id)
            )
            t = ETBETransformation()
            if e.parent_tx is None:
                t.previous_stock = LotTransaction.objects.get(lot=e.lot.parent_lot)
            else:
                t.previous_stock = e.parent_tx
            t.new_stock = e
            t.volume_ethanol = e.lot.parent_lot.volume
            t.volume_etbe = e.lot.volume
            assert t.new_stock.lot.parent_lot == t.previous_stock.lot
            assert t.new_stock.lot != t.previous_stock.lot
            t.save()
    # check that for all transformation, new_stock.parent_tx = previous_stock
    # and new_stock.lot.parent_lot = previous_stock.lot
    transformations = ETBETransformation.objects.all()
    for t in transformations:
        if t.new_stock.parent_tx_id != t.previous_stock.id:
            print("Transformation link error")
            print(
                "New stock %s parent tx %s previous stock %s"
                % (t.new_stock.id, t.new_stock.parent_tx_id, t.previous_stock.id)
            )

        new_stock_parent_lot_id = t.new_stock.lot.parent_lot_id
        old_stock_lot_id = t.previous_stock.lot_id
        if new_stock_parent_lot_id != old_stock_lot_id:
            print(
                "New Stock tx id %s Previous tx id %s New Stock Parent Tx id %s"
                % (t.new_stock.id, t.previous_stock.id, t.new_stock.parent_tx_id)
            )
            print(
                "New lot id %s previous %s new parent lot %s. Update with %s"
                % (t.new_stock.lot.id, t.previous_stock.lot.id, t.new_stock.lot.parent_lot_id, old_stock_lot_id)
            )
            # update
            new_lot = t.new_stock.lot
            new_lot.parent_lot_id = old_stock_lot_id
            new_lot.save()
