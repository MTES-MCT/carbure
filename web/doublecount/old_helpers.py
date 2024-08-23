import datetime

import openpyxl
import pandas as pd
from django.http import JsonResponse

from core.common import get_sheet_data
from core.models import Biocarburant, MatierePremiere, Pays
from doublecount.models import DoubleCountingProduction, DoubleCountingSourcing

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
    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.filter(is_double_compte=True)}
    countries = {f.code_pays: f for f in Pays.objects.all()}

    DoubleCountingSourcing.objects.filter(dca=dca).delete()
    for idx, row in sourcing_data.iterrows():
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
        dcs.save()


def load_dc_production_data(dca, production_data):
    feedstocks = {f.code: f for f in MatierePremiere.objects.filter(is_double_compte=True)}
    biofuels = {f.code: f for f in Biocarburant.objects.all()}

    DoubleCountingProduction.objects.filter(dca=dca).delete()
    for idx, row in production_data.iterrows():
        feedstock = feedstocks.get(row.feedstock, None)
        biofuel = biofuels.get(row.biofuel, None)
        dcs = DoubleCountingProduction(dca=dca)
        dcs.year = row.year
        dcs.feedstock = feedstock
        dcs.biofuel = biofuel
        dcs.max_production_capacity = row.max_production_capacity
        dcs.estimated_production = row.estimated_production
        dcs.requested_quota = row.requested_quota
        dcs.save()


def load_dc_recognition_file(entity, psite_id, user, filepath):
    return JsonResponse({"status": "error", "message": "not implemented"}, status=400)
