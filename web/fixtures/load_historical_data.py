import datetime
import os

import django
import openpyxl
from django.contrib.auth import get_user_model
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

usermodel = get_user_model()
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, Pays

default_eec_values = {
    "ETHBETTERAVE": 12,
    "ETHBLE": 23,
    "ETHMAIS": 20,
    "ETHCANNE_A_SUCRE": 14,
    "ETBEBETTERAVE": 12,
    "ETBEBLE": 23,
    "ETBEMAIS": 20,
    "ETBECANNE_A_SUCRE": 14,
    "EMHVCOLZA": 29,
    "EMHVTOURNESOL": 18,
    "EMHVSOJA": 19,
    "EMHVHUILE_PALME": 14,
    "EMHUHUILE_ALIMENTAIRE_USAGEE": 0,
    "HVOGCOLZA": 30,
    "HVOGTOURNESOL": 18,
    "HVOGHUILE_PALME": 15,
    "HVOECOLZA": 30,
    "HVOETOURNESOL": 18,
    "HVOEHUILE_PALME": 15,
    "HVOCOLZA": 30,
    "HVOTOURNESOL": 18,
    "HVOHUILE_PALME": 15,
}

# load data
producers = {p.name.upper(): p for p in Entity.objects.filter(entity_type="Producteur")}
Entity.objects.update_or_create(name="ATLANTIC ENERGY", entity_type=Entity.OPERATOR)
Entity.objects.update_or_create(name="TRANSCOR", entity_type=Entity.OPERATOR)
Entity.objects.update_or_create(name="OMNEO FRANCE", entity_type=Entity.OPERATOR)
operators = {p.name.upper(): p for p in Entity.objects.filter(entity_type="Opérateur")}
# company aliases
operators["AOT ENERGIE"] = operators["AOT"]
operators["ESAF"] = operators["ESSO SAF"]
operators["ARGOS OIL FRANCE"] = operators["VARO MAG"]
operators["ARGOS OIL"] = operators["VARO MAG"]
operators["ARGOS TRADING"] = operators["VARO MAG"]
operators["ESSO"] = operators["ESSO SAF"]
operators["TRANSCOR FRANCE"] = operators["TRANSCOR"]
operators["SHELL"] = operators["SOCIETE DES PETROLES SHELL (SPS)"]
operators["SOCIETE DES PETROLES SHELL"] = operators["SOCIETE DES PETROLES SHELL (SPS)"]
operators["VARO ENERGY FR"] = operators["VARO ENERGY"]
operators["TOTAL RAFFINAGE France"] = operators["TERF"]
operators["TRF"] = operators["TERF"]
operators["TOTAL MARKETING France"] = operators["TMF"]
operators["FAL DISTRI"] = operators["FAL DISTRI SAS"]
operators["BOLLORE ENERGY"] = operators["BOLLORE"]
operators["CPA (RUBIS TERMINAL)"] = operators["CPA"]
operators["EFR"] = operators["EG RETAIL"]
operators["EFR FRANCE"] = operators["EG RETAIL"]
operators["EFR FRANCE (EX DELEK)"] = operators["EG RETAIL"]
operators["THEVENIN-DUCROT"] = operators["THEVENIN DUCROT"]
operators["THEVENIN & DUCROT"] = operators["THEVENIN DUCROT"]
operators["GINOUVES"] = operators["GINOUVES GEORGES"]
operators["PETROLES DE LA COTE BASQUE"] = operators["PCB"]
operators["VEMAG"] = operators["VARO MAG"]
operators["VEST"] = operators["VARO MAG"]
operators["URBAINE DES PETROLES"] = operators["UDP"]
operators["URBAINE DES PÉTROLES"] = operators["UDP"]
operators["PETROVEX"] = operators["AUCHAN ENERGIES"]
operators["PÉTROVEX"] = operators["AUCHAN ENERGIES"]
operators["TEREOS"] = producers["TEREOS ORIGNY"]
operators["RAISINOR"] = producers["RAISINOR"]
operators["SAIPOL"] = producers["SAIPOL"]
operators["BOLLORÉ ENERGIE"] = operators["BOLLORE"]
operators["BOLLORE ENERGIE"] = operators["BOLLORE"]
operators["ENI FRANCE"] = operators["ENI"]
operators["PÉTROLE ET DÉRIVÉS"] = operators["SCAPED"]
operators["TOTAL MARKETING FRANCE"] = operators["TMF"]
operators["TOTAL RAFFINAGE FRANCE"] = operators["TERF"]
operators["TOTAL RF"] = operators["TERF"]
operators["TOTAL R F"] = operators["TERF"]
operators["VARO ENERGY FRANCE"] = operators["VARO MAG"]
operators["WALLACH"] = operators["VARO MAG"]
operators["TOTAL MS"] = operators["TMF"]


MatierePremiere.objects.update_or_create(code="PFAD", name="PFAD", name_en="PFAD", is_displayed=False)
mps = {mp.code: mp for mp in MatierePremiere.objects.all()}
mps["RÉSIDUS DE TRANSFORMATION FORESTIÈRE"] = mps["DECHETS_BOIS"]
mps["MATIÈRE CELLULOSIQUE : COUVERT FORESTIER À COURTE ROTATION"] = mps["DECHETS_BOIS"]
mps["CANOLA"] = mps["COLZA"]
mps["NOYAU DE PALMISTE"] = mps["PFAD"]

bcs = {bc.code: bc for bc in Biocarburant.objects.all()}
bcs["HVHTG"] = bcs["HVOG"]
bcs["HVHTE"] = bcs["HVOE"]
bcs["HVO"] = bcs["HVOG"]
bcs["ETHANOL"] = bcs["ETH"]
countries = {c.code_pays: c for c in Pays.objects.all()}
france = Pays.objects.get(code_pays="FR")

today = datetime.date.today()
now = datetime.datetime.now()
mtes = Entity.objects.get(name="MTE - DGEC")


def load_lot(lot):
    # {'Opérateur': 'UDP', 'producer': None, 'production_site': None, 'production_site_country': 'NL', 'production_site_reference': 'EU-ISCC-Cert-DE100-17452019', 'production_site_commissioning_date': datetime.datetime(2008, 11, 29, 0, 0), 'double_counting_registration': None, 'vendor': None, 'volume': 2242.0, 'biocarburant_code': 'EMHV', 'matiere_premiere_code': 'COLZA', 'pays_origine_code': 'UA', 'eec': None, 'el': None, 'ep': 38.9, 'etd': 1.0, 'eu': None, 'esca': None, 'eccs': None, 'eccr': None, 'eee': None, 'dae': '19BEK4AP7G7V00EGNBHL4', 'champ_libre': None, 'delivery_date': datetime.datetime(2019, 12, 18, 0, 0), 'delivery_site': None, 'Total des émissions de GES': 39.9}  # noqa: E501
    if lot["dae"] is None:
        dae = "UNKNOWN"
    dae = str(lot["dae"])

    op = lot["Opérateur"]
    if not op:
        print("missing operator")
        print(lot)
        return
    lop = op.upper()
    if lop not in operators:
        print("Could not find operator %s in operators" % (lop))
        return
    op = operators[lop]

    lc = lot["production_site_country"]
    if lc is not None and lc != "":
        lc = lc.upper().strip()
    else:
        if "FR" in dae:
            lc = "FR"
        else:
            # can we find it somehow?
            if (
                lot["double_counting_registration"] is not None
                and isinstance(lot["double_counting_registration"], str)
                and lot["double_counting_registration"][0:2] in countries
            ):
                lc = lot["double_counting_registration"][0:2]
            else:
                # assume produced in france
                lc = "FR"
    if lc != "":
        upsc = countries[lc]
    else:
        print("Could not find lot country")
        print(lot)
    lupscd = lot["production_site_commissioning_date"]
    if lupscd is None:
        lupscd = datetime.datetime(year=2008, month=10, day=5)
    elif type(lupscd) == type(today) or type(lupscd) == type(now):
        # do nothing
        pass
    # float and integers
    elif type(lupscd) == type(0.01) or type(lupscd) == type(2000):
        if lupscd > 1950 and lupscd < 2050:
            lupscd = datetime.datetime(year=int(lupscd), month=1, day=1)
        else:
            print("lupscd is an unknown float, ignoring line: %f" % (lupscd))
            print(dae)
            return
    elif type(lupscd) == type("str"):
        lupscd = lupscd.strip().lower()
        if lupscd.startswith("avant "):
            lupscd = datetime.datetime.strptime(lupscd[6:].strip(), "%Y-%m-%d") - datetime.timedelta(days=1)
        elif lupscd.startswith("après "):
            lupscd = datetime.datetime.strptime(lupscd[6:].strip(), "%Y-%m-%d") + datetime.timedelta(days=1)
        else:
            try:
                lupscd = datetime.datetime.strptime(lupscd, "%d/%m/%Y")
            except Exception:
                try:
                    lupscd = datetime.datetime.strptime(lupscd, "%d-%m-%Y")
                except Exception:
                    print("could not parse date %s" % (lupscd))
                    return
    else:
        print("Unknown type for production site com date: %s %s %s" % (lupscd, type(lupscd), type(now)))
        return

    dd = lot["delivery_date"]
    if isinstance(dd, str):
        try:
            year = int(dd[6:10])
            if year < 20:
                year += 2000
            month = int(dd[3:5])
            day = int(dd[0:2])
            dd = datetime.datetime(year=year, month=month, day=day)
        except Exception:
            print("could not load date")
            print(dd)
            print(lot)
            return
    if dd is None:
        dd = datetime.datetime(2014, 1, 1)
    if isinstance(dd, int):
        dd = datetime.date.fromordinal(datetime.datetime(1900, 1, 1).toordinal() + lot["delivery_date"] - 2)
    try:
        dd.strftime("%Y-%m")
    except Exception:
        print("delivery date problem")
        print(lot)
        return
    d = {
        "period": dd.year * 100 + dd.month,
        "year": dd.year,
        "carbure_producer": None,
        "unknown_producer": "",
        "carbure_production_site": None,
        "unknown_production_site": "",
        "production_country": upsc,
        "production_site_commissioning_date": lupscd,
        "production_site_certificate": lot["production_site_reference"],
        "production_site_double_counting_certificate": lot["double_counting_registration"],
        "carbure_supplier": None,
        "unknown_supplier": None,
        "carbure_client": op,
        "delivery_date": dd,
        "transport_document_reference": dae,
    }
    cert = lot.get("supplier_certificate", "")
    if cert is not None:
        d["supplier_certificate"] = cert[0:63]
    vol = lot["volume"]
    if isinstance(vol, str):
        vol = vol.replace(",", "").replace(" ", "")
        try:
            vol = float(vol)
        except Exception:
            print("Could not load volume: %s" % (vol))
            return
    if vol == 0 or vol is None:
        print("Missing volume")
        print(lot)
        return
    bc = lot["biocarburant_code"]
    if not bc:
        print("No biofuel, ignoring")
        print(lot)
        return
    lbc = bc.upper()
    if lbc == "ET":
        lbc = "ETH"
    if lbc not in bcs:
        print("Could not find biofuel %s" % (lbc))
        print(lot)
        return
    bc = bcs[lbc]
    lmp = lot["matiere_premiere_code"]
    if lmp:
        lmp = lmp.upper()
    else:
        print("Missing matiere premiere:")
        print("Could not load lot %s" % (lot))
    if lmp not in mps:
        print("Could not find matiere_premiere %s" % (lmp))
        return
    mp = mps[lmp]
    po = lot["pays_origine_code"]
    if po is not None:
        lpo = lot["pays_origine_code"].upper()
    else:
        lpo = ""
    if lpo not in countries:
        print("Could not find country of origin %s - assuming france" % (lpo))
        lpo = "FR"
    d["country_of_origin"] = countries[lpo]
    ##### GES
    ### case 1: ep and etd are defined
    try:
        d["ep"] = float(lot["ep"])
        d["etd"] = float(lot["etd"])
        d["ghg_total"] = d["ep"] + d["etd"]
        eec_key = bc.code + mp.code
        if eec_key in default_eec_values:
            eec = default_eec_values[eec_key]
            if d["ep"] - eec < 0:
                pass
            else:
                d["eec"] = eec
                d["ep"] -= eec
    except Exception:
        ### else only take GES TOTAL
        ghg_total = lot["GES TOTAL"]
        if isinstance(ghg_total, str):
            ghg_total = ghg_total.replace(",", ".")
            try:
                ghg_total = float(ghg_total)
                d["ghg_total"] = ghg_total
            except Exception:
                print("could not parse ghg value %s" % (ghg_total))
                print(lot)
                return
        else:
            d["ghg_total"] = ghg_total
    if d["ghg_total"] is None:
        print("NONE GES")
        print(lot)
        return
    d["ghg_reference"] = 83.8
    d["ghg_total"] = round(d["ghg_total"], 2)
    d["ghg_reduction"] = round((1.0 - (d["ghg_total"] / d["ghg_reference"])) * 100.0, 2)
    d["lot_status"] = CarbureLot.FROZEN
    d["added_by"] = mtes
    d["free_field"] = "import carbure"

    obj = CarbureLot(**d)
    obj.biofuel = bc
    obj.feedstock = mp
    obj.volume = vol
    obj.delivery_type = CarbureLot.BLENDING
    # obj.save()
    return obj


def load_file(year, filename, delete=False):
    if delete:
        lots = CarbureLot.objects.filter(added_by=mtes, year=year, free_field="import carbure").delete()
        print(lots)
        return

    wb = openpyxl.load_workbook(filename, data_only=True)
    lots_sheet = wb["Feuil1"]
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
    print("File processed, loading batches")
    to_save = []
    for lot in tqdm(lots):
        lot = load_lot(lot)
        if lot is None:
            continue
        to_save.append(lot)
        if len(to_save) > 100:
            CarbureLot.objects.bulk_create(to_save)
            to_save = []


def load_histo_data():
    files = [
        (2018, "2018lotsv2.xlsx"),
        (2017, "2017lotsv2.xlsx"),
        (2016, "2016lotsv2.xlsx"),
        (2015, "2015lotsv2.xlsx"),
        (2014, "2014lotsv2.xlsx"),
    ]
    for year, f in files:
        print("Loading file %s" % (f))
        load_file(year, f, delete=True)


if __name__ == "__main__":
    load_histo_data()
