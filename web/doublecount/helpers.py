import datetime
import openpyxl
import pandas as pd
from django.http import JsonResponse, HttpResponse
from core.models import Pays, Biocarburant, MatierePremiere
from doublecount.models import DoubleCountingAgreement, DoubleCountingSourcing, DoubleCountingProduction

today = datetime.date.today()

def load_dc_sourcing_file(entity, psite_id, user, filepath):
    start = datetime.date(today.year + 1, 1, 1)
    end = datetime.date(today.year + 2, 12, 31)

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.filter(is_double_compte=True)}
    countries = {f.code_pays: f for f in Pays.objects.all()}
    try:
        wb = openpyxl.load_workbook(file, data_only=True)
        sheet = wb.worksheets['sourcing']
        column_names = data[0]
        data = data[1:]
        df = pd.DataFrame(data, columns=column_names)
        df.fillna('', inplace=True)
        dca, created = DoubleCountingAgreement.objects.get_or_create(producer=entity, production_site_id=psite_id, period_start=start, period_end=end)
        DoubleCountingSourcing.objects.filter(dca=dca).delete()
        for idx, row in df.iterrows():
            print(row)
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
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': "something went wrong"}, status=400)

    return JsonResponse({'status': 'success', 'data': data})

def load_dc_production_file(entity, psite_id, user, filepath):
    start = datetime.date(today.year + 1, 1, 1)
    end = datetime.date(today.year + 2, 12, 31)
    feedstocks = {f.code: f for f in MatierePremiere.objects.filter(is_double_compte=True)}
    countries = {f.code_pays: f for f in Pays.objects.all()}
    biofuels = {f.code: f for f in Biocarburant.objects.all()}

    try:
        wb = openpyxl.load_workbook(file, data_only=True)
        sheet = wb.worksheets['production']
        column_names = data[0]
        data = data[1:]
        df = pd.DataFrame(data, columns=column_names)
        df.fillna('', inplace=True)
        dca, created = DoubleCountingAgreement.objects.get_or_create(producer=entity, production_site_id=psite_id, period_start=start, period_end=end)
        DoubleCountingSourcing.objects.filter(dca=dca).delete()
        for idx, row in df.iterrows():
            print(row)
            feedstock = feedstocks.get(row.feedstock, None)
            biofuel = biofuels.get(row.biofuel, None)
            dcs = DoubleCountingProduction(dca=dca)
            dcs.year = row.year
            dcs.feedstock = feedstock
            dcs.biofuel = biofuel
            dcs.metric_tonnes=row.metric_tonnes
            dcs.save()
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': "something went wrong"}, status=400)  

def load_dc_recognition_file(entity, psite_id, user, filepath):
    return JsonResponse({'status': 'error', 'message': 'not implemented'}, status=400)        

