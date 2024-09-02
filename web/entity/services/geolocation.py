import requests

URL = "http://api-adresse.data.gouv.fr/search/"


def get_coordinates(address):
    params = {"q": address, "limit": 1}
    response = requests.get(URL, params=params)
    results = response.json()

    if len(results.get("features")) > 0:
        first_result = results.get("features")[0]
        lon, lat = first_result.get("geometry").get("coordinates")
        return lon, lat
    else:
        return None
