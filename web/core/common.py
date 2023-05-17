import datetime
from urllib import response
from django.http import JsonResponse
import openpyxl
import numpy as np
import os
from multiprocessing import Process
from time import perf_counter

import pandas as pd
from pandas._typing import Scalar
from typing import List

from core.carburetypes import Carbure, CarbureUnit

from core.models import CarbureLot, GenericCertificate, Biocarburant
from core.models import TransactionDistance
from core.ign_distance import get_distance

from certificates.models import DoubleCountingRegistration
from certificates.models import DoubleCountingRegistration

july1st2021 = datetime.date(year=2021, month=7, day=1)


def try_get_certificate(certificate):
    d = {
        "holder": "",
        "valid_until": "",
        "valid_from": "",
        "matches": 0,
        "found": False,
        "certificate_id": certificate,
        "certificate_type": "",
    }
    matches = GenericCertificate.objects.filter(certificate_id=certificate)
    count = matches.count()
    if count == 0:
        return d
    if count > 1:
        d["matches"] = count
        return d
    d["matches"] = 1
    d["found"] = True
    if count == 1:
        c = matches[0]
        d["holder"] = c.certificate_holder
        d["valid_until"] = c.valid_until
        d["valid_from"] = c.valid_from
        d["certificate_type"] = c.certificate_type
    return d


def try_get_double_counting_certificate(cert):
    d = {
        "holder": "",
        "valid_until": "",
        "valid_from": "",
        "matches": 0,
        "found": False,
        "certificate_type": "DC",
        "certificate_id": cert,
    }
    matches = DoubleCountingRegistration.objects.filter(certificate_id=cert)
    count = matches.count()
    d["matches"] = count
    if count == 0:
        return d
    elif count > 1:
        return d
    else:
        c = matches[0]
        d["found"] = True
        d["holder"] = c.certificate_holder
        d["valid_from"] = c.valid_from
        d["valid_until"] = c.valid_until
    return d


def get_uploaded_files_directory():
    directory = "/app/files"
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            return "/tmp"
    return directory


def calculate_ghg(lot, tx=None):
    lot.ghg_total = (
        lot.eec
        + lot.el
        + lot.ep
        + lot.etd
        + lot.eu
        - lot.esca
        - lot.eccs
        - lot.eccr
        - lot.eee
    )
    lot.ghg_reference = 83.8
    lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)
    lot.ghg_reference_red_ii = 94.0
    lot.ghg_reduction_red_ii = round(
        (1.0 - (lot.ghg_total / lot.ghg_reference_red_ii)) * 100.0, 2
    )


def convert_cell(cell, convert_float: bool) -> Scalar:
    from openpyxl.cell.cell import TYPE_BOOL, TYPE_ERROR, TYPE_NUMERIC

    if cell.is_date:
        return cell.value
    elif cell.data_type == TYPE_ERROR:
        return np.nan
    elif cell.data_type == TYPE_BOOL:
        return bool(cell.value)
    elif cell.value is None:
        return ""  # compat with xlrd
    elif cell.data_type == TYPE_NUMERIC:
        # GH5394
        if convert_float:
            val = int(cell.value)
            if val == cell.value:
                return val
        else:
            return float(cell.value)

    return cell.value


def get_sheet_data(sheet, convert_float: bool) -> List[List[Scalar]]:
    data: List[List[Scalar]] = []
    for row in sheet.rows:
        data.append(
            [
                convert_cell(cell, convert_float)
                if isinstance(cell, openpyxl.cell.cell.Cell)
                else ""
                for cell in row
            ]
        )
    return data


def get_transaction_distance(tx):
    url_link = "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=driving"
    res = {"distance": -1, "link": "", "error": None, "source": None}

    if not tx.lot.production_site_is_in_carbure:
        res["error"] = "PRODUCTION_SITE_NOT_IN_CARBURE"
        return res
    if not tx.delivery_site_is_in_carbure:
        res["error"] = "DELIVERY_SITE_NOT_IN_CARBURE"
        return res
    starting_point = tx.lot.carbure_production_site.gps_coordinates
    delivery_point = tx.carbure_delivery_site.gps_coordinates

    if not starting_point:
        res["error"] = "PRODUCTION_SITE_COORDINATES_NOT_IN_CARBURE"
        return res
    if not delivery_point:
        res["error"] = "DELIVERY_SITE_COORDINATES_NOT_IN_CARBURE"
        return res
    try:
        td = TransactionDistance.objects.get(
            starting_point=starting_point, delivery_point=delivery_point
        )
        res["link"] = url_link % (starting_point, delivery_point)
        res["distance"] = td.distance
        res["source"] = "DB"
        return res
    except:
        # not found
        # launch in parallel
        p = Process(target=get_distance, args=(starting_point, delivery_point))
        p.start()
        res["error"] = "DISTANCE_NOT_IN_CACHE"
        return res


def convert_template_row_to_formdata(entity, prefetched_data, filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheet = wb.worksheets[0]
    data = get_sheet_data(sheet, convert_float=True)
    column_names = data[0]
    data = data[1:]
    df = pd.DataFrame(data, columns=column_names)
    df.fillna("", inplace=True)
    lots_data = []
    for row in df.iterrows():
        lot_row = row[1]
        lot = {}
        if lot_row.get("volume", "") == "" and (
            lot_row.get("unit", "") == "" or lot_row.get("quantity", "") == ""
        ):
            # ignore rows with no volume or no unit+quantity
            # this is mostly done to ignore entirely empty rows read in the excel/csv file
            # without this, we can receive dozens of empty rows...
            continue
        # TEMPLATE COLUMNS
        # 'champ_libre',
        # 'producer', 'production_site', 'production_site_reference', 'production_site_country', 'production_site_commissioning_date', 'double_counting_registration',
        # 'supplier', 'supplier_certificate', ('vendor_certificate') removed,
        # 'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
        # 'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee',
        # 'dae', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country', 'delivery_type']

        # TARGET COLUMNS
        # free_field, carbure_producer, unknown_producer, carbure_production_site, unknown_production_site
        # production_country, production_site, commissioning_date, production_site_certificate, production_site_double_counting_certificate
        # carbure_supplier, unknown_supplier, supplier_certificate
        # transport_document, carbure_client, unknown_client, delivery_date, carbure_delivery_site, unknown_delivery_site, delivery_site_country
        # biofuel, feedstock, country_of_origin

        lot["carbure_stock_id"] = lot_row.get("carbure_stock_id", "").strip()
        lot["free_field"] = lot_row.get("champ_libre", "")
        producer = lot_row.get("producer", "").strip()
        production_site = lot_row.get("production_site", "").strip()
        if (
            producer is None
            or producer == ""
            or producer.upper() == entity.name.upper()
        ) and production_site.upper() in prefetched_data["my_production_sites"]:
            # I am the producer
            lot["carbure_production_site"] = production_site
            # carbure_supplier and carbure_producer will be set to entity in construct_carbure_lot
        else:
            # I am not the producer
            lot["unknown_producer"] = producer
            lot["unknown_production_site"] = production_site
            lot["production_country_code"] = lot_row.get(
                "production_site_country", None
            )
            lot["production_site_commissioning_date"] = lot_row.get(
                "production_site_commissioning_date", ""
            )
            lot["unknown_supplier"] = lot_row.get("supplier", "")
        lot["production_site_certificate"] = lot_row.get(
            "production_site_reference", ""
        )
        lot["production_site_double_counting_certificate"] = lot_row.get(
            "double_counting_registration", ""
        )
        lot["vendor_certificate"] = lot_row.get("vendor_certificate", "")
        lot["supplier_certificate"] = lot_row.get("supplier_certificate", "")
        lot["volume"] = lot_row.get("volume", 0)
        lot["quantity"] = lot_row.get("quantity", 0)
        lot["unit"] = lot_row.get("unit", None)
        lot["feedstock_code"] = lot_row.get("matiere_premiere_code", "").strip()
        lot["biofuel_code"] = lot_row.get("biocarburant_code", "").strip()
        lot["country_code"] = lot_row.get("pays_origine_code", "").strip()
        lot["delivery_type"] = lot_row.get("delivery_type", CarbureLot.UNKNOWN)
        for key in ["el"]:  # negative value allowed
            try:
                lot[key] = float(lot_row.get(key, 0))
            except:
                lot[key] = 0
        for key in [
            "eec",
            "ep",
            "etd",
            "eu",
            "esca",
            "eccs",
            "eccr",
            "eee",
        ]:  # positive value only
            try:
                lot[key] = abs(float(lot_row.get(key, 0)))
            except:
                lot[key] = 0
        lot["transport_document_reference"] = lot_row.get("dae", "")
        lot["delivery_date"] = lot_row.get("delivery_date", "")
        delivery_site = str(lot_row.get("delivery_site", ""))
        if delivery_site.upper() in prefetched_data["depots"]:
            lot["carbure_delivery_site_depot_id"] = prefetched_data["depots"][
                delivery_site.upper()
            ].depot_id
        elif delivery_site.upper() in prefetched_data["depotsbyname"]:
            lot["carbure_delivery_site_depot_id"] = prefetched_data["depotsbyname"][
                delivery_site.upper()
            ].depot_id
        else:
            lot["unknown_delivery_site"] = delivery_site
            delivery_site_country = lot_row.get("delivery_site_country", "")
            lot["delivery_site_country_code"] = delivery_site_country.strip()
        client = lot_row.get("client", "").upper().strip()
        if client in prefetched_data["clientsbyname"]:
            lot["carbure_client_id"] = prefetched_data["clientsbyname"][client].id
        else:
            lot["unknown_client"] = client
        lots_data.append(lot)
    return lots_data


def ErrorResponse(status_code, error=None, data=None):
    response_data = {}
    response_data["status"] = Carbure.ERROR
    if data is not None:
        response_data["data"] = data
    if error is not None:
        response_data["error"] = error
    return JsonResponse(response_data, status=status_code)


def SuccessResponse(data=None):
    response_data = {}
    response_data["status"] = Carbure.SUCCESS
    if data is not None:
        response_data["data"] = data
    return JsonResponse(response_data)


# based on a given biofuel, convert any quantity type into all others
def compute_quantities(
    biofuel: Biocarburant,
    quantity=None,
    unit=None,
    volume=None,
    weight=None,
    lhv_amount=None,
):
    # normalize the given data in the form of a (quantity, unit) couple
    if quantity is not None:
        quantity = round(float(quantity), 2)
        unit = (unit or CarbureUnit.LITER).lower()
    elif volume is not None:
        quantity = round(float(volume), 2)
        unit = CarbureUnit.LITER
    elif weight is not None:
        quantity = round(float(weight), 2)
        unit = CarbureUnit.KILOGRAM
    elif lhv_amount is not None:
        quantity = round(float(lhv_amount), 2)
        unit = CarbureUnit.LHV
    else:
        raise Exception("No quantity was specified")

    # compute the different quantity values based on the previous config
    if unit == CarbureUnit.LITER:
        volume = quantity
        weight = round(volume * biofuel.masse_volumique, 2)
        lhv_amount = round(volume * biofuel.pci_litre, 2)
    elif unit == CarbureUnit.KILOGRAM:
        weight = quantity
        volume = round(weight / biofuel.masse_volumique, 2)
        lhv_amount = round(volume * biofuel.pci_litre, 2)
    elif unit == CarbureUnit.LHV:
        lhv_amount = quantity
        volume = round(lhv_amount / biofuel.pci_litre, 2)
        weight = round(volume * biofuel.masse_volumique, 2)

    return volume, weight, lhv_amount


# little helper to help measure elapsed time
class Perf:
    def __init__(self, message="Start"):
        self.steps = []
        self.step(message)

    def step(self, message):
        t = perf_counter()
        tLast = self.steps[-1] if len(self.steps) > 0 else t
        dt = t - tLast
        self.steps.append(t)
        print("[%f] %s" % (dt, message))

    def done(self, message="Done"):
        self.step(message)


class CarbureException(Exception):
    def __init__(self, error, meta=None):
        self.error = error
        self.meta = meta or {}
        super().__init__()

    def __str__(self):
        return f"CarbureException: Error code {self.error}. Meta: {self.meta}"
