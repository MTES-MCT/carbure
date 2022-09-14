import datetime
import openpyxl
import pandas as pd
from django.http import JsonResponse
from core.models import Pays, Biocarburant, MatierePremiere
from core.common import get_sheet_data
from doublecount.models import DoubleCountingSourcing, DoubleCountingProduction
from doublecount.dc_sanity_checks import check_production_line, check_sourcing_line

today = datetime.date.today()


def load_dc_file(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)

    sourcing_sheet = wb["sourcing"]
    sourcing_data = get_sheet_data(sourcing_sheet, convert_float=True)
    sourcing_column_names = sourcing_data[0]
    sourcing_data = sourcing_data[1:]
    sourcing_df = pd.DataFrame(sourcing_data, columns=sourcing_column_names)
    sourcing_df.fillna("", inplace=True)

    production_sheet = wb["production"]
    production_data = get_sheet_data(production_sheet, convert_float=True)
    production_column_names = production_data[0]
    production_data = production_data[1:]
    production_df = pd.DataFrame(production_data, columns=production_column_names)
    production_df.fillna("", inplace=True)

    return sourcing_df, production_df


def load_dc_sourcing_data(dca, sourcing_data):
    # prepare error list
    errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    countries = {f.code_pays: f for f in Pays.objects.all()}

    DoubleCountingSourcing.objects.filter(dca=dca).delete()
    for idx, row in sourcing_data.iterrows():
        # skip rows that start empty
        if not row.year:
            continue
        feedstock = feedstocks.get(row.feedstock, None)
        origin_country = countries.get(row.origin_country, None)
        supply_country = countries.get(row.supply_country, None)
        transit_country = countries.get(row.transit_country, None)
        dcs = DoubleCountingSourcing(dca=dca)
        dcs.year = row.year
        dcs.feedstock = feedstock
        dcs.origin_country = origin_country
        dcs.supply_country = supply_country
        dcs.transit_country = transit_country
        dcs.metric_tonnes = row.metric_tonnes
        dcs_errors = check_sourcing_line(dcs, row, idx + 2)
        errors += dcs_errors
        if len(dcs_errors) == 0:
            dcs.save()

    return errors


def load_dc_production_data(dca, production_data):
    # prepare error list
    errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    biofuels = {f.code: f for f in Biocarburant.objects.all()}

    DoubleCountingProduction.objects.filter(dca=dca).delete()
    for idx, row in production_data.iterrows():
        # skip rows that start empty
        if not row.year:
            continue

        feedstock = feedstocks.get(row.feedstock, None)
        biofuel = biofuels.get(row.biofuel, None)
        dcp = DoubleCountingProduction(dca=dca)
        dcp.year = row.year
        dcp.feedstock = feedstock
        dcp.biofuel = biofuel
        dcp.max_production_capacity = row.max_production_capacity
        dcp.estimated_production = row.estimated_production
        dcp.requested_quota = row.requested_quota
        dcp_errors = check_production_line(dcp, row, idx + 2)
        errors += dcp_errors
        if len(dcp_errors) == 0:
            dcp.save()

    return errors


def load_dc_recognition_file(entity, psite_id, user, filepath):
    return JsonResponse({"status": "error", "message": "not implemented"}, status=400)
