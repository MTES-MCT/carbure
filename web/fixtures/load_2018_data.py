import datetime
import os

import django
import openpyxl
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

usermodel = get_user_model()
from core.models import Biocarburant, Entity, LotTransaction, LotV2, MatierePremiere, Pays

# load data
producers = {p.name:p for p in Entity.objects.filter(entity_type='Producteur')}
Entity.objects.update_or_create(name='ATLANTIC ENERGY', entity_type=Entity.OPERATOR)
operators = {p.name:p for p in Entity.objects.filter(entity_type='Opérateur')}
# company aliases
operators['AOT ENERGIE'] = operators['AOT']
operators['ESAF'] = operators['ESSO SAF']
operators['SHELL'] = operators['Societe des Petroles Shell (SPS)']
operators['VARO ENERGY FR'] = operators['VARO ENERGY']
operators['TOTAL RAFFINAGE France'] = operators['TRF']
operators['TOTAL MARKETING France'] = operators['TMF']
operators['FAL DISTRI'] = operators['FAL DISTRI SAS']
operators['GINOUVES'] = operators['GINOUVES GEORGES']
operators['PETROLES DE LA COTE BASQUE'] = operators['PCB']
operators['VEMAG'] = operators['VARO MAG']
operators['PETROVEX'] = operators['AUCHAN ENERGIES']
operators['TEREOS'] = producers['TEREOS Origny']
operators['RAISINOR'] = producers['RAISINOR']
operators['SAIPOL'] = producers['SAIPOL']


MatierePremiere.objects.update_or_create(code='PFAD', name='PFAD', name_en='PFAD', is_displayed=False)
mps = {mp.code:mp for mp in MatierePremiere.objects.all()}
bcs = {bc.code:bc for bc in Biocarburant.objects.all()}
bcs['HVHTG'] = bcs['HVOG']
bcs['HVHTE'] = bcs['HVOE']
countries = {c.code_pays:c for c in Pays.objects.all()}


today = datetime.date.today()
now = datetime.datetime.now()
mtes = Entity.objects.get(name='MTE - DGEC')
try:
    robot = usermodel.objects.get(name='MTE Robot 2018')
except:
    usermodel.objects.create_user(name='MTE Robot 2018', email='robot2018@carbure.beta.gouv.fr')
    robot = usermodel.objects.get(name='MTE Robot 2018')

france = Pays.objects.get(code_pays='FR')

r = LotV2.objects.filter(added_by_user=robot).delete()

filename = '%s/web/fixtures/2018lotsv2.xlsx' % (os.environ['CARBURE_HOME'])

wb = openpyxl.load_workbook(filename)
lots_sheet = wb['Feuil1']
colid2field = {}
lots = []
# create a dictionary from the line
for i, row in enumerate(lots_sheet):
    if i == 0:
        # header
        for i, col in enumerate(row):
            colid2field[i] = col.value
    else:
        lot = {}
        for i, col in enumerate(row):
            field = colid2field[i]
            lot[field] = col.value
        lots.append(lot)

for i, lot in enumerate(lots):
    # {'Opérateur': 'UDP', 'producer': None, 'production_site': None, 'production_site_country': 'NL', 'production_site_reference': 'EU-ISCC-Cert-DE100-17452019', 'production_site_commissioning_date': datetime.datetime(2008, 11, 29, 0, 0), 'double_counting_registration': None, 'vendor': None, 'volume': 2242.0, 'biocarburant_code': 'EMHV', 'matiere_premiere_code': 'COLZA', 'pays_origine_code': 'UA', 'eec': None, 'el': None, 'ep': 38.9, 'etd': 1.0, 'eu': None, 'esca': None, 'eccs': None, 'eccr': None, 'eee': None, 'dae': '19BEK4AP7G7V00EGNBHL4', 'champ_libre': None, 'delivery_date': datetime.datetime(2019, 12, 18, 0, 0), 'delivery_site': None, 'Total des émissions de GES': 39.9}
    if lot['dae'] is None:
        dae = 'UNKNOWN'
    dae = str(lot['dae'])

    lop = lot['Opérateur']
    if lop not in operators:
        print('Could not find operator %s in operators' % (lop))
        continue
    op = operators[lop]
    lc = lot['production_site_country']
    if lc is not None and lc != '':
        lc = lc.upper().strip()
    else:
        if dae.startswith('18FR'):
            lc = 'FR'
        else:
            # can we find it somehow?
            if lot['double_counting_registration'] is not None and lot['double_counting_registration'][0:2] in countries:
                lc = lot['double_counting_registration'][0:2]
            else:
                # assume produced in france
                lc = 'FR'
    if lc != '':
        upsc = countries[lc]
    else:
        print('Could not load lot %s' % (lot))
    lupscd = lot['production_site_commissioning_date']
    if type(lupscd) != type(today) and type(lupscd) != type(now):
        if lupscd == None:
            lupscd = datetime.datetime(year=2008, month=10, day=5)
        # float and integers
        elif type(lupscd) == type(0.01) or type(lupscd) == type(2000):
            if lupscd > 1950 and lupscd < 2050:
                lupscd = datetime.datetime(year=int(lupscd), month=1, day=1)
            else:
                print('lupscd is an unknown float, ignoring line: %f' % (lupscd))
                print(dae)
                continue
        elif type(lupscd) == type('str'):
            lupscd = lupscd.strip().lower()
            if lupscd.startswith('avant '):
                lupscd = datetime.datetime.strptime(lupscd[6:].strip(), '%Y-%m-%d') - datetime.timedelta(days=1)
            elif lupscd.startswith('après '):
                lupscd = datetime.datetime.strptime(lupscd[6:].strip(), '%Y-%m-%d') + datetime.timedelta(days=1)
            else:
                try:
                    lupscd = datetime.datetime.strptime(lupscd, '%d/%m/%Y')
                    #lupscd = dateutil.parser.parse(lupscd, dayfirst=true)
                except:
                    try:
                        lupscd = datetime.datetime.strptime(lupscd, '%d-%m-%Y')
                    except:
                        print('could not parse date %s' % (lupscd))
                        continue
                #try:
                #    year = int(lupscd[0:4])
                #    month = int(lupscd[5:7])
                #    day = int(lupscd[8:10])
                #    lupscd = datetime.date(year=year, month=month, day=day)
                #except:
                #    print('Could not get production site com date: %s %s' % (lupscd, type(lupscd)))
                #    continue
        else:
            print('Unknown type for production site com date: %s %s' % (lupscd, type(lupscd)))
            continue

    dd = lot['delivery_date']
    if isinstance(dd, str):
        year = int(dd[6:10])
        month = int(dd[3:5])
        day = int(dd[0:2])
        dd = datetime.datetime(year=year, month=month, day=day)
        #dd = dateutil.parser.parse(dd, dayfirst=True)
    if dd is None:
        dd = datetime.datetime(2018, 1, 1)
    try:
        period = dd.strftime('%Y-%m')
    except:
        print('delivery date problem')
        print(lot)
        continue
    d = {'period': period, 'year':dd.year,
         'producer_is_in_carbure': False, 'carbure_producer': None, 'unknown_producer':'',
         'production_site_is_in_carbure': False, 'carbure_production_site': None,
         'unknown_production_site': '',
         'unknown_production_country': upsc,
         'unknown_production_site_com_date': lupscd,
         'unknown_production_site_reference': lot['production_site_reference'],
         'unknown_production_site_dbl_counting': lot['double_counting_registration'],
    }
    vol = lot['volume']
    lbc = lot['biocarburant_code'].upper()
    if lbc == 'ET':
        lbc = 'ETH'
    if lbc not in bcs:
        print('Could not find biocarburant %s' % (lbc))
        print(lot)
        continue
    bc = bcs[lbc]
    lmp = lot['matiere_premiere_code']
    if lmp:
        lmp = lmp.upper()
    else:
        print('Missing matiere premiere:')
        print('Could not load lot %s' % (lot))
    if lmp not in mps:
        print('Could not find matiere_premiere %s' % (lmp))
        continue
    mp = mps[lmp]
    lpo = lot['pays_origine_code'].upper()
    if lpo not in countries:
        print('Could not find country %s' % (lpo))
        continue
    d['pays_origine'] = countries[lpo]
    d['ep'] = lot['ep'] if type(lot['ep']) == 'float' else 0
    d['etd'] = lot['etd'] if type(lot['etd']) == 'float' else 0
    d['ghg_total'] = lot['GES TOTAL']
    d['ghg_reference'] = 83.8
    if d['ghg_total'] is None:
        if d['ep'] + d['etd'] > 0:
            d['ghg_total'] = d['ep'] + d['etd']
        else:
            print('GHG TOTAL is NONE')
            print(lot)
            continue
    ghg_total = float(d['ghg_total'])
    d['ghg_reduction'] = round((1.0 - (ghg_total / d['ghg_reference'])) * 100.0, 2)
    d['status'] = 'Validated'
    d['source'] = 'EXCEL'
    d['added_by'] = mtes
    d['added_by_user'] = robot
    d['data_origin_entity'] = mtes
    obj = LotV2(**d)
    obj.biocarburant = bc
    obj.matiere_premiere = mp
    obj.volume = vol
    try:
        obj.save()
    except Exception as e:
        print("Could not create lot %s" % (e))
        print(lot)
        continue

    tx = LotTransaction()
    tx.lot = obj
    tx.vendor_is_in_carbure = False
    tx.carbure_vendor = None
    tx.unknown_vendor = ''
    tx.dae = dae
    tx.client_is_in_carbure = True
    tx.carbure_client = op
    tx.unknown_client = ''
    tx.delivery_date = dd
    tx.delivery_site_is_in_carbure = False
    tx.carbure_delivery_site = None
    tx.unknown_delivery_site = ''
    tx.unknown_delivery_site_country = france
    tx.delivery_status = 'F'
    try:
        tx.save()
        print('created lot %d' % (i), end='\r')
    except Exception as e:
        print('could not create lot %s' % (lot))
        print(e)

