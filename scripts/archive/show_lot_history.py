import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


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


def show_tx_and_parents(tx):
    if tx.parent_tx:
        show_tx_and_parents(tx.parent_tx)
    pretty_print(tx)


def show_tx_and_child(tx):
    pretty_print(tx)

    child = LotTransaction.objects.filter(parent_tx=tx)
    if child:
        for c in child:
            show_tx_and_child(c)


def show_lot_and_child(id):
    tx = LotTransaction.objects.get(id=id)

    show_tx_and_parents(tx)
    child = LotTransaction.objects.filter(parent_tx=tx, lot__status="Validated")
    child_volume = 0
    for c in child:
        show_tx_and_child(c)
        child_volume += c.lot.volume

    print(
        "Parent volume [%d] remaining [%d] theo remaining [%d] diff [%d] child volume [%d]"
        % (
            tx.lot.volume,
            tx.lot.remaining_volume,
            tx.lot.volume - child_volume,
            tx.lot.remaining_volume - (tx.lot.volume - child_volume),
            child_volume,
        )
    )


if __name__ == "__main__":
    show_lot_and_child(id=int(sys.argv[1]))
