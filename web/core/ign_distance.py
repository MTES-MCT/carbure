import requests
import json
import os
import argparse
from requests.auth import HTTPBasicAuth

user = os.environ.get("IGN_USER", False)
pwd = os.environ.get("IGN_PWD", False)
cle = os.environ.get("IGN_KEY", False)

def get_distance(a, b):  
    #transformation orthographique des coordonnées
    alat,alon = a.replace(' ', '').split(',')
    blat,blon = b.replace(' ', '').split(',')
  
    e = "%s,%s" % (alon, alat)
    s = "%s,%s" % (blon, blat)
  
    # Construction de l'URL
    url = "http://wxs.ign.fr/%s/itineraire/rest/route.json?origin=%s&destination=%s&method=DISTANCE&graphName=Voiture" % (cle, e, s)
  
    # Récupération de la réponse
    res = requests.get(url, auth=HTTPBasicAuth(user, pwd)).json()
    distance = res['distance'].replace(' Km', '')
    print(distance)

#itineraire("49.5087332809, 0.534041811072","49.1693649378,-0.310691187417")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate distance in Km from two gps points')
    parser.add_argument('start', action='store')
    parser.add_argument('end', action='store')
    args = parser.parse_args()
    get_distance(args.start, args.end)
