import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core import serializers

from core.models import *


def snapshot_feyzin_data():
    trans = ETBETransformation.objects.all()
    serialized_obj = serializers.serialize('json', trans)
    f = open('transformations.json', 'w')
    f.write(serialized_obj)
    f.close()

if __name__ == '__main__':
    snapshot_feyzin_data()
