from typing import Any

import requests

URL = "http://api-adresse.data.gouv.fr/search/"
REQUEST_TIMEOUT_SECONDS = 5

ADDRESS_FIELDS = ("address", "postal_code", "city", "country_id")


def get_coordinates(address: str) -> tuple[float, float] | None:
    params = {"q": address, "limit": 1}
    try:
        response = requests.get(URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError):
        return None

    features = results.get("features")
    if not features:
        return None

    geometry = features[0].get("geometry") or {}
    coordinates = geometry.get("coordinates")
    if not coordinates:
        return None

    lon, lat = coordinates
    return lat, lon


def build_site_address(site) -> str | None:
    parts = [site.address, site.postal_code, site.city]
    has_precise_address = any(part and str(part).strip() for part in parts)
    if not has_precise_address:
        return None
    if site.country:
        parts.append(site.country.name)
    address = " ".join(part.strip() for part in parts if part and str(part).strip())
    return address or None


def resolve_gps_coordinates(address: str) -> str | None:
    if not address:
        return None

    coords = get_coordinates(address)

    if not coords:
        return None

    lat, lon = coords
    return f"{lat},{lon}"


def site_address_changed(site, previous_values: dict[str, Any] | None) -> bool:
    if previous_values is None:
        return False
    return any(previous_values[field] != getattr(site, field) for field in ADDRESS_FIELDS)
