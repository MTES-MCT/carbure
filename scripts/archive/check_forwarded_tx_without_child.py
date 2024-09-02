import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


def check_odd_forward():
    lots = LotTransaction.objects.filter(is_forwarded=True)
    for l in lots:
        try:
            child = LotTransaction.objects.get(parent_tx=l)
        except:
            print(
                "Missing child for txid %d. Period %s Sender %s Client %s"
                % (
                    l.id,
                    l.lot.period,
                    l.carbure_vendor.name if l.carbure_vendor else l.lot.unknown_supplier,
                    l.carbure_client.name if l.carbure_client else l.unknown_client,
                )
            )
            # check with lot
            missing_child = LotTransaction.objects.filter(lot=l.lot).exclude(id=l.id)
            if missing_child.count() > 0:
                # N transactions with the same lot, link them together
                parent_id = l.id
                for child in missing_child:
                    child.parent_tx_id = parent_id
                    print("Adding parent_tx %d to child %d" % (l.id, child.id))
                    child.save()
                    parent_id = child.id
            else:
                # cancel forward
                l.is_forwarded = False
                l.save()


if __name__ == "__main__":
    check_odd_forward()
