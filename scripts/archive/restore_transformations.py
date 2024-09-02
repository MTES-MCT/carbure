import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core import serializers  # noqa: E402

from core.models import *  # noqa: E402


def load_feyzin_data():
    trans = {tx.id: tx for tx in ETBETransformation.objects.all()}

    prev_trans = []
    f = open("transformations.json", "r")
    it = serializers.deserialize("json", f)
    for obj in it:
        prev_trans.append(obj)
    f.close()

    for tx in prev_trans:
        if tx.object.id not in trans:
            print("restoring transformation %d" % (tx.object.id))
            tx.save()


if __name__ == "__main__":
    load_feyzin_data()
