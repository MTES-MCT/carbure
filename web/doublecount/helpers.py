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
    errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    countries = {f.code_pays: f for f in Pays.objects.all()}

    DoubleCountingSourcing.objects.filter(dca=dca).delete()
    for row in sourcing_rows:
        # skip rows that start empty
        if not row["year"]:
            continue
        feedstock = feedstocks.get(row["feedstock"], None) if row["feedstock"] else None
        origin_country = countries.get(row["origin_country"], None) if row["origin_country"] else None
        supply_country = countries.get(row["supply_country"], None) if row["supply_country"] else None
        transit_country = countries.get(row["transit_country"], None) if row["transit_country"] else None
        dcs = DoubleCountingSourcing(dca=dca)
        dcs.year = row["year"]
        if feedstock:
            dcs.feedstock = feedstock
        if origin_country:
            dcs.origin_country = origin_country
        dcs.supply_country = supply_country
        dcs.transit_country = transit_country
        dcs.metric_tonnes = row["metric_tonnes"]
        dcs_errors = check_sourcing_row(dcs, row)
        errors += dcs_errors
        if len(dcs_errors) == 0:
            dcs.save()

    return errors


def load_dc_production_data(dca: DoubleCountingAgreement, production_rows: List[ProductionRow]):
    # prepare error list
    errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    biofuels = {f.code: f for f in Biocarburant.objects.all()}

    DoubleCountingProduction.objects.filter(dca=dca).delete()
    for row in production_rows:
        # skip rows that start empty
        if not row["year"]:
            continue

        feedstock = feedstocks.get(row["feedstock"], None)
        biofuel = biofuels.get(row["biofuel"], None)
        dcp = DoubleCountingProduction(dca=dca)
        dcp.year = row["year"]
        dcp.feedstock = feedstock
        dcp.biofuel = biofuel
        dcp.max_production_capacity = row["max_production_capacity"]
        dcp.estimated_production = row["estimated_production"]
        dcp.requested_quota = row["requested_quota"]
        dcp_errors = check_production_row(dcp, row)
        errors += dcp_errors
        if len(dcp_errors) == 0:
            dcp.save()

    return errors


def load_dc_recognition_file(entity, psite_id, user, filepath):
    return JsonResponse({"status": "error", "message": "not implemented"}, status=400)
