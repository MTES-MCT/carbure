import argparse
import json
import traceback

import requests
from django import db

from core.models import TransactionDistance


def get_distance(a, b):
    #transformation orthographique des coordonnées
    alat,alon = a.replace(' ', '').split(',')
    blat,blon = b.replace(' ', '').split(',')

    e = "%s,%s" % (alon, alat)
    s = "%s,%s" % (blon, blat)

    # Construction de l'URL
    url = """https://wxs.ign.fr/calcul/geoportail/itineraire/rest/1.0.0/route?resource=bdtopo-osrm&start=%s&end=%s&profile=car&optimization=fastest&constraints=%%7B%%22constraintType%%22%%3A%%22banned%%22%%2C%%22key%%22%%3A%%22wayType%%22%%2C%%22operator%%22%%3A%%22%%3D%%22%%2C%%22value%%22%%3A%%22autoroute%%22%%7D&getSteps=false&getBbox=false&distanceUnit=kilometer&timeUnit=hour&crs=EPSG%%3A4326""" % (s, e)

    # Récupération de la réponse
    try:
        res = requests.get(url)
        res = json.loads(res.text)
    except Exception as e:
        traceback.print_exc()
        return 'ERROR'
    distance = res['distance']
    db.connections.close_all()
    TransactionDistance.objects.update_or_create(starting_point=a, delivery_point=b, defaults={'distance':distance})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate distance in Km from two gps points')
    parser.add_argument('start', action='store')
    parser.add_argument('end', action='store')
    args = parser.parse_args()
    distance = get_distance(args.start, args.end)
    print(distance)
