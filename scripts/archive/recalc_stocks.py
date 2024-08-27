import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

transformations = ETBETransformation.objects.all()
transformed_in = [e.previous_stock_id for e in transformations]


def pretty_print(tx):
    print(
        "Tx [%d] Parent Tx [%s] Lot [%d] Parent Lot [%s] %s %s %d (remaining %d) From %s To %s [Period %s - %s] Forwarded: %s Stock: %s"  # noqa: E501
        % (
            tx.id,
            tx.parent_tx_id,
            tx.lot.id,
            tx.lot.parent_lot_id,
            tx.lot.biocarburant.name,
            tx.lot.matiere_premiere.name,
            tx.lot.volume,
            tx.lot.remaining_volume,
            tx.lot.carbure_producer.name if tx.lot.carbure_producer else tx.lot.unknown_producer,
            tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
            tx.lot.period,
            tx.delivery_date,
            tx.is_forwarded,
            tx.is_stock,
        )
    )


def reset_remaining_volume(tx):
    if tx.id in transformed_in:
        if not tx.lot.is_transformed:
            print("ignoring ETBE stock. marking lot as transformed")
            tx.lot.is_transformed = True
            tx.lot.save()
        return

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
    if tx.lot.is_transformed:
        print("ignoring ETBE")
        return
    if tx.id in transformed_in:
        print("ignoring ETBE stock + marking lot as transformed")
        tx.lot.is_transformed = True
        tx.lot.save()
        return

    sum_volume = 0
    for c in child_tx:
        # pretty_print(c)
        # if c.is_forwarded:
        #    continue
        sum_volume += c.lot.volume
    diff = round(tx.lot.volume - sum_volume, 2) - round(tx.lot.remaining_volume, 2)
    if abs(diff) > 0.1:
        print(
            "Parent volume [%d] remaining [%d] theo remaining [%d] diff [%d] child volume [%d]"
            % (
                tx.lot.volume,
                tx.lot.remaining_volume,
                tx.lot.volume - sum_volume,
                tx.lot.remaining_volume - (tx.lot.volume - sum_volume),
                sum_volume,
            )
        )
        print("Tx id [%d] Lot Id [%d]" % (tx.id, tx.lot.id))
        print(
            "Parent remaining_volume != initial volume - child volume: Lot initial volume [%f] Sum of child [%f] Remaining [%f] Theo Remaining [%f] Diff [%f]"  # noqa: E501
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
        if input("Save?") == "y":
            print("Saving")
            tx.lot.save()
        print("New remaining volume: [%f]" % (tx.lot.remaining_volume))


def fix_other_stock():
    # ensure forwarded lots are marked as such
    lots_with_parent = LotV2.objects.filter(parent_lot__isnull=False)
    for l in lots_with_parent:
        tx = LotTransaction.objects.filter(lot=l)
        parent_tx = LotTransaction.objects.filter(lot=l.parent_lot)
        if tx.count() > 1 or parent_tx.count() > 1:
            parent = parent_tx[0]
            for t in parent_tx:
                print("PARENT", t.id, t.lot_id, t.lot.biocarburant.name, t.lot.volume, t.carbure_client, t.delivery_date)
            for t in tx:
                print(t.id, t.lot_id, t.lot.biocarburant.name, t.lot.volume, t.carbure_client, t.delivery_date, t.parent_tx)
                if t.parent_tx is None:
                    if tx.count() == 1:
                        print("Marking Parent tx as %d" % (parent.id))
                        t.parent_tx_id = parent.id
                        t.save()
                        if parent.lot.biocarburant != t.lot.biocarburant:
                            print("Marking Parent lot as transformed")
                            parent.lot.is_transformed = True
                            parent.lot.save()
                    else:
                        print("Parent tx should be %d" % (parent.id))
                        x = input("Continue")
                        if x == "y":
                            t.parent_tx_id = parent.id
                            t.save()
                            if parent.lot.biocarburant != t.lot.biocarburant:
                                print("Marking Parent lot as transformed")
                                parent.lot.is_transformed = True
                                parent.lot.save()
                        else:
                            print("You said NO")
                            raise AssertionError()
                parent = t
        if tx.count() == 1 and parent_tx.count() == 1:
            # pretty sure this is a forward
            ptx = parent_tx[0]
            ctx = tx[0]
            if ptx.lot.volume != ctx.lot.volume:
                continue
            # if not ptx.is_forwarded:
            #    print('Update tx id %d. Set is forwarded = True. Child tx %d' % (ptx.id, ctx.id))
            #    ptx.is_forwarded = True
            #    ptx.save()
            if not ctx.parent_tx:
                print(
                    "Update tx id %d. Set parent_tx %d. Client 1 %s Client 2 %s"
                    % (
                        ctx.id,
                        ptx.id,
                        ptx.carbure_client.name,
                        ctx.carbure_client.name if ctx.carbure_client else ctx.unknown_client,
                    )
                )
                ctx.parent_tx = ptx
                ctx.save()
    del lots_with_parent

    # fix links between sublots and lots
    txs = LotTransaction.objects.filter(lot__parent_lot__isnull=False, parent_tx__isnull=True)
    for tx in txs:
        print("Tx %d Lot %d has parent lot %d but not parent tx" % (tx.id, tx.lot.id, tx.lot.parent_lot_id))
        potential_parents = LotTransaction.objects.filter(lot_id=tx.lot.parent_lot.id)
        if potential_parents.count() == 1:
            tx.parent_tx = potential_parents[0]
            tx.save()
            print("Fix link between parent %s and child %s" % (potential_parents[0].id, tx.id))
        else:
            print("Could not find parent for tx id %d lot id %d parent lot id %d" % (tx.id, tx.lot.id, tx.lot.parent_lot_id))

    stocks = LotTransaction.objects.filter(
        lot__status="Validated", is_stock=True, is_forwarded=False, lot__is_transformed=False
    )
    for l in stocks:
        child_txs = LotTransaction.objects.filter(parent_tx=l, lot__status="Validated")
        if l.carbure_client and l.carbure_client.entity_type == Entity.OPERATOR:
            print("Client is an operator. Should not happen")
            if child_txs.count() == 0:
                print("No sub tx, unmark as stock")
                print(
                    l.id,
                    l.lot.period,
                    l.lot.volume,
                    l.lot.remaining_volume,
                    l.lot.biocarburant.code,
                    l.lot.matiere_premiere.code,
                    l.carbure_client.name if l.carbure_client else l.unknown_client,
                )
                if l.lot.volume == l.lot.remaining_volume:
                    # mark as blending
                    l.is_stock = False
                    l.save()
            else:
                if child_txs.count() == 1:
                    print("Operator stock with one children")
                    print("should be marked as processing")
                    l.is_forwarded = True
                    l.save()
                else:
                    print("Operator stock with more than one transaction, need investigation")
                    print(l.id, l.lot.id)
                    print(child_txs)
                    raise AssertionError()
            continue
        if child_txs.count() == 0:
            if l.is_mac:
                print("SHOULD NOT HAPPEN. CANNOT DO is_stock + is_mac")
                if l.lot.volume == l.lot.remaining_volume:
                    # mark as blending
                    l.is_stock = False
                    l.save()
                reset_remaining_volume(l)
            else:
                if not l.lot.is_transformed:
                    reset_remaining_volume(l)
        else:
            handle_complex_stock(l, child_txs)


if __name__ == "__main__":
    fix_other_stock()
