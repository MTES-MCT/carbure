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
producers = {p.name: p for p in Entity.objects.filter(entity_type="Producteur")}
operators = {p.name: p for p in Entity.objects.filter(entity_type="Opérateur")}
operators["Shell Trading Rotterdam"] = operators["Societe des Petroles Shell (SPS)"]
operators["TEREOS Origny"] = Entity.objects.get(name="TEREOS Origny")
operators["SAIPOL"] = Entity.objects.get(name="SAIPOL")
operators["RAISINOR"] = Entity.objects.get(name="RAISINOR")

mps = {mp.code: mp for mp in MatierePremiere.objects.all()}
bcs = {bc.code: bc for bc in Biocarburant.objects.all()}
countries = {c.code_pays: c for c in Pays.objects.all()}
today = datetime.date.today()
now = datetime.datetime.now()
mtes = Entity.objects.get(name="MTE - DGEC")
# usermodel.objects.create_user(name='MTE Robot 2020', email='robot2020@carbure.beta.gouv.fr')
robot = usermodel.objects.get(name="MTES Robot 2020")
france = Pays.objects.get(code_pays="FR")

r = LotV2.objects.filter(added_by_user=robot).delete()
print(r)

filename = "%s/web/fixtures/2020db.xlsx" % (os.environ["CARBURE_HOME"])

wb = openpyxl.load_workbook(filename)
lots_sheet = wb["lots2"]
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
            if isinstance(col.value, str):
                lot[field] = col.value.replace("\u202f", "").replace("\xa0", " ")
            else:
                lot[field] = col.value
        lots.append(lot)


for i, lot in enumerate(lots):
    if lot["dae"] is None:
        lot["dae"] = "MISSING_DAE"

    lop = lot["Opérateur"]
    if lop not in operators:
        print("Could not find operator %s in operators" % (lop))
        continue
    op = operators[lop]
    lc = lot["production_site_country"]
    if lc is not None:
        lc = lc.upper()
    else:
        if lot["double_counting_registration"] and lot["double_counting_registration"][0:2] in countries:
            lc = lot["double_counting_registration"][0:2]
        else:
            print("Could not find double counting prefix country %s %s" % (lot["double_counting_registration"], lc))
            print(lot)
            continue
    if lc != "":
        upsc = countries[lc]
    else:
        print("Could not load lot %s" % (lot))
    lupscd = lot["production_site_commissioning_date"]
    if type(lupscd) != type(today) and type(lupscd) != type(now):
        if lupscd == None:
            lupscd = datetime.datetime(year=2008, month=10, day=5)
        # float and integers
        elif type(lupscd) == type(0.01) or type(lupscd) == type(2000):
            if lupscd > 1940 and lupscd < 2050:
                lupscd = datetime.datetime(year=int(lupscd), month=1, day=1)
            else:
                print("lupscd is an unknown float, ignoring line: %f" % (lupscd))
                print(lot["dae"])
                print(lot)
                continue
        elif type(lupscd) == type("str"):
            lupscd = lupscd.strip().lower()
            if lupscd.startswith("avant "):
                lupscd = datetime.datetime.strptime(lupscd[6:].strip(), "%d/%m/%Y") - datetime.timedelta(days=1)
            elif lupscd.startswith("après "):
                lupscd = datetime.datetime.strptime(lupscd[6:].strip(), "%d/%m/%Y") + datetime.timedelta(days=1)
            elif lupscd.lower().startswith("anterieur au "):
                lupscd = datetime.datetime.strptime(lupscd[13:].strip(), "%d/%m/%Y") - datetime.timedelta(days=1)
            elif lupscd.lower().startswith("postérieur au "):
                lupscd = datetime.datetime.strptime(lupscd[14:].strip(), "%d/%m/%Y") + datetime.timedelta(days=1)
            else:
                try:
                    lupscd = datetime.datetime.strptime(lupscd, "%d/%m/%Y")
                except:
                    print("Could not get production site com date: [%s] %s" % (lupscd, type(lupscd)))
                    continue
        else:
            print("Unknown type for production site com date: %s %s" % (lupscd, type(lupscd)))
            continue

    d = {
        "period": "",
        "producer_is_in_carbure": False,
        "carbure_producer": None,
        "unknown_producer": "",
        "production_site_is_in_carbure": False,
        "carbure_production_site": None,
        "unknown_production_site": "",
        "unknown_production_country": upsc,
        "unknown_production_site_com_date": lupscd,
        "unknown_production_site_reference": lot["production_site_reference"],
        "unknown_production_site_dbl_counting": lot["double_counting_registration"],
    }
    if isinstance(lot["delivery_date"], datetime.date) or isinstance(lot["delivery_date"], datetime.datetime):
        d["period"] = lot["delivery_date"].strftime("%Y-%m")
        delivery_date = lot["delivery_date"]
        # d['year'] = lot['delivery_date'].year
    else:
        try:
            dd = datetime.datetime.strptime(lot["delivery_date"], "%d/%m/%Y").date()
            d["period"] = dd.strftime("%Y-%m")
            delivery_date = dd
            # d['year'] = dd.year
        except:
            print("unknown delivery_date type %s or format %s" % (lot["delivery_date"], type(lot["delivery_date"])))
            print(lot)
            continue
    try:
        if isinstance(lot["volume"], str):
            vol = float(lot["volume"].replace(" ", ""))
        elif isinstance(lot["volume"], int):
            vol = lot["volume"]
        else:
            vol = float(lot["volume"])
    except:
        print("Could not parse volume")
        print("%s - [%s]" % (type(lot["volume"]), lot["volume"]))
        print(lot)
        continue
    lbc = lot["biocarburant_code"].upper()
    if lbc == "ET":
        lbc = "ETH"
    if lbc not in bcs:
        print("Could not find biocarburant %s" % (lbc))
        continue
    bc = bcs[lbc]
    lmp = lot["matiere_premiere_code"]
    if lmp:
        lmp = lmp.upper()
    else:
        print("Missing matiere premiere:")
        print("Could not load lot %s" % (lot))
    if lmp not in mps:
        print("Could not find matiere_premiere %s" % (lmp))
        continue
    mp = mps[lmp]
    lpo = lot["pays_origine_code"]
    if lpo:
        lpo = lpo.upper()
    else:
        print("Missing pays origine")
        print(lot)
        continue
    if lpo not in countries:
        print("Could not find country %s" % (lpo))
        continue
    d["pays_origine"] = countries[lpo]
    d["ep"] = lot["ep"] if type(lot["ep"]) == "float" else 0
    d["etd"] = lot["etd"] if type(lot["etd"]) == "float" else 0
    d["ghg_total"] = lot["GES TOTAL"]
    if isinstance(d["ghg_total"], str):
        d["ghg_total"] = float(d["ghg_total"].replace(",", ".").replace(" ", ""))
    d["ghg_reference"] = 83.8
    if d["ghg_total"] is None:
        if d["ep"] + d["etd"] > 0:
            d["ghg_total"] = d["ep"] + d["etd"]
        else:
            print("GHG TOTAL is NONE")
            print(lot["dae"])
            continue
    d["ghg_reduction"] = round((1.0 - (d["ghg_total"] / d["ghg_reference"])) * 100.0, 2)
    d["status"] = "Validated"
    d["source"] = "EXCEL"
    d["added_by"] = mtes
    d["added_by_user"] = robot
    d["data_origin_entity"] = mtes
    obj = LotV2(**d)
    obj.biocarburant = bc
    obj.matiere_premiere = mp
    obj.volume = vol
    obj.save()
    tx = LotTransaction()
    tx.lot = obj
    tx.vendor_is_in_carbure = False
    tx.carbure_vendor = None
    tx.unknown_vendor = ""
    tx.dae = lot["dae"]
    tx.client_is_in_carbure = True
    tx.carbure_client = op
    tx.unknown_client = ""
    tx.delivery_date = delivery_date
    tx.delivery_site_is_in_carbure = False
    tx.carbure_delivery_site = None
    tx.unknown_delivery_site = ""
    tx.unknown_delivery_site_country = france
    tx.delivery_status = "F"
    if tx.carbure_client.entity_type == "Producteur":
        tx.is_mac = True
    try:
        tx.save()
    except Exception as e:
        print("Could not save lot %d %s" % (i, lot))
        print(e)
    print("created lot %d" % (i), end="\r")
