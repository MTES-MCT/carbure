import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, MatierePremiere, Pays, Biocarburant, CarbureLot

def load_eec_data():
    pass

def load_ep_data():
    pass

def load_etd_data():
    pass

if __name__ == '__main__':
    load_eec_data()
    load_ep_data()
    load_etd_data()
