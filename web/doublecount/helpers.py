import datetime
from typing import List
from django.http import JsonResponse
from core.models import Pays, Biocarburant, MatierePremiere
from doublecount.models import DoubleCountingSourcing, DoubleCountingProduction
from doublecount.dc_sanity_checks import check_production_row, check_sourcing_row
from doublecount.models import DoubleCountingAgreement
from doublecount.dc_parser import SourcingRow, ProductionRow


today = datetime.date.today()


def load_dc_sourcing_data(dca: DoubleCountingAgreement, sourcing_rows: List[SourcingRow]):
    # prepare error list
    sourcing_data = []
    sourcing_errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    countries = {f.code_pays: f for f in Pays.objects.all()}

    for row in sourcing_rows:
        # skip rows that start empty
        if not row["year"]:
            continue
        feedstock = feedstocks.get(row["feedstock"], None) if row["feedstock"] else None
        origin_country = countries.get(row["origin_country"], None) if row["origin_country"] else None
        supply_country = countries.get(row["supply_country"], None) if row["supply_country"] else None
        transit_country = countries.get(row["transit_country"], None) if row["transit_country"] else None
        sourcing = DoubleCountingSourcing(dca=dca)
        sourcing.year = row["year"]
        if feedstock:
            sourcing.feedstock = feedstock
        if origin_country:
            sourcing.origin_country = origin_country
        sourcing.supply_country = supply_country
        sourcing.transit_country = transit_country
        sourcing.metric_tonnes = row["metric_tonnes"]
        errors = check_sourcing_row(sourcing, row)
        sourcing_errors += errors
        if len(errors) == 0:
            sourcing_data.append(sourcing)

    return sourcing_data, sourcing_errors


def load_dc_production_data(dca: DoubleCountingAgreement, production_rows: List[ProductionRow]):
    production_data = []
    production_errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    biofuels = {f.code: f for f in Biocarburant.objects.all()}

    for row in production_rows:
        # skip rows that start empty
        if not row["year"]:
            continue

        feedstock = feedstocks.get(row["feedstock"], None)
        biofuel = biofuels.get(row["biofuel"], None)
        production = DoubleCountingProduction(dca=dca)
        production.year = row["year"]
        production.feedstock = feedstock
        production.biofuel = biofuel
        production.max_production_capacity = row["max_production_capacity"]
        production.estimated_production = row["estimated_production"]
        production.requested_quota = row["requested_quota"]

        errors = check_production_row(production, row)
        production_errors += errors
        if len(errors) == 0:
            production_data.append(production)

    return production_data, production_errors


def load_dc_recognition_file(entity, psite_id, user, filepath):
    return JsonResponse({"status": "error", "message": "not implemented"}, status=400)
