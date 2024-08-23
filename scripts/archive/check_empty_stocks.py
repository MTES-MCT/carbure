import os

import django
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *


def reset_remaining_volume(tx):
    if tx.lot.volume != tx.lot.remaining_volume:
        print(
            "Reset %s remaining volume from %f to %f. Tx id [%d] Lot id [%d] client %s"
            % (
                tx.lot.biocarburant.code,
                tx.lot.remaining_volume,
                tx.lot.volume,
                tx.id,
                tx.lot.id,
                tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
            )
        )
        tx.lot.remaining_volume = tx.lot.volume
        tx.lot.save()


def handle_complex_stock(tx, child_tx):
    sum_child = child_tx.filter(is_forwarded=False).aggregate(Sum("lot__volume"))
    sum_volume = sum_child["lot__volume__sum"]
    if not sum_volume:
        sum_volume = 0
    diff = round(tx.lot.volume - sum_volume, 2) - round(tx.lot.remaining_volume, 2)
    if abs(diff) > 0.1:
        if tx.lot.biocarburant.code == "ETH":
            return
        print(
            "Parent remaining_volume != initial volume - child volume: Lot initial volume [%f] Sum of child [%f] Remaining [%f] Theo Remaining [%f] Diff [%f]"
            % (tx.lot.volume, sum_volume, tx.lot.remaining_volume, tx.lot.volume - sum_volume, diff)
        )
        print(
            "Original Lot Period [%s] Volume [%f] BC [%s] MP [%s] Client [%s]"
            % (
                tx.lot.period,
                tx.lot.volume,
                tx.lot.biocarburant.code,
                tx.lot.matiere_premiere.code,
                tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
            )
        )
        for c in child_tx:
            print(
                "Child txid %d Lot Period [%s] Volume [%f] BC [%s] MP [%s] Client [%s]"
                % (
                    c.id,
                    c.lot.period,
                    c.lot.volume,
                    c.lot.biocarburant.code,
                    c.lot.matiere_premiere.code,
                    c.carbure_client.name if c.carbure_client else c.unknown_client,
                )
            )
        print("Readjusting remaining volume to %f" % (tx.lot.volume - sum_volume))
        tx.lot.remaining_volume = tx.lot.volume - sum_volume
        tx.lot.save()
        print("New remaining volume: [%f]" % (tx.lot.remaining_volume))


def fix_etbe():
    transformations = ETBETransformation.objects.all()
    for t in transformations:
        if t.previous_stock.id == t.new_stock.id:
            orig_lot = t.new_stock.lot.parent_lot
            orig_tx = LotTransaction.objects.filter(lot=orig_lot).order_by("-id")[0]
            t.previous_stock = orig_tx
            t.save()
            print(
                "Fixed ETBE Transformation %d. Previous stock: %d New Stock %d" % (t.id, t.previous_stock.id, t.new_stock.id)
            )

    txs = LotTransaction.objects.filter(lot__year=2021, lot__status="Validated", lot__biocarburant__code="ETBE")
    for t in txs:
        try:
            initial_eth_stock_line = ETBETransformation.objects.get(new_stock=t).previous_stock
            transformations = ETBETransformation.objects.filter(previous_stock=initial_eth_stock_line)

            total_volume_converted_to_etbe = 0
            for t in transformations:
                total_volume_converted_to_etbe += t.volume_ethanol

            total_volume_sent_as_eth = 0
            child = LotTransaction.objects.filter(
                lot__parent_lot=initial_eth_stock_line.lot, lot__biocarburant__code="ETH", lot__status="Validated"
            )
            for c in child:
                total_volume_sent_as_eth += c.lot.volume

            theo_remaining = initial_eth_stock_line.lot.volume - total_volume_converted_to_etbe - total_volume_sent_as_eth
            remaining = initial_eth_stock_line.lot.remaining_volume
            diff = theo_remaining - remaining
            if abs(diff) > 0.1:
                print(
                    "Original Stock Line volume [%f] remaining [%f] theo remaining [%f] diff [%f]"
                    % (initial_eth_stock_line.lot.volume, initial_eth_stock_line.lot.remaining_volume, theo_remaining, diff)
                )
                print(
                    "ETH transformed into ETBE [%f], sent directly [%f]"
                    % (total_volume_converted_to_etbe, total_volume_sent_as_eth)
                )
                initial_eth_stock_line.lot.remaining_volume = theo_remaining
                initial_eth_stock_line.lot.save()
        except:
            continue


def fix_other_stock():
    stocks = LotTransaction.objects.filter(lot__year=2021, lot__status="Validated")
    for l in stocks:
        child_txs = LotTransaction.objects.filter(lot__parent_lot=l.lot, lot__status="Validated")
        if child_txs.count() == 0:
            if l.carbure_client and l.carbure_client.entity_type == Entity.OPERATOR:
                # no doubts here. the remaining volume should be equal to volume
                reset_remaining_volume(l)
            elif l.is_mac:
                # same here
                reset_remaining_volume(l)
            else:
                if not l.lot.is_transformed:
                    reset_remaining_volume(l)
        else:
            handle_complex_stock(l, child_txs)


if __name__ == "__main__":
    fix_etbe()
    fix_other_stock()
