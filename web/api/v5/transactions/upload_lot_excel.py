import datetime
import dateutil
import difflib
import numpy
import openpyxl
import pandas
import traceback
import unicodedata

from django.db import transaction
from core.decorators import check_user_rights
from core.common import get_uploaded_files_directory, SuccessResponse, ErrorResponse
from core.models import CarbureLot, Entity, Biocarburant, MatierePremiere, Depot, Pays, GenericCertificate
from producers.models import ProductionSite
from core.serializers import CarbureLotPublicSerializer, GenericErrorSerializer
from core.carburetypes import CarbureUnit
from api.v4.sanity_checks import bulk_sanity_checks, generic_error


@check_user_rights()
def upload_lot_excel(request, *args, **kwargs):
    entity_id = request.POST.get("entity_id")
    excel_file = request.FILES.get("file")

    try:
        entity = Entity.objects.get(pk=entity_id)

        file_path = save_excel_file(excel_file, entity)
        lot_rows = parse_excel_file(file_path)

        with transaction.atomic():
            backwards_compatible_rows = [backwards_compatibility(row) for row in lot_rows]
            parsed_rows = [parse_fields(row) for row in backwards_compatible_rows]
            matched_rows = enrich_data(parsed_rows, entity)
            enriched_rows = [fill_defaults(row, entity) for row in matched_rows]
            lots = create_lots(enriched_rows, entity)

            errors = bulk_sanity_checks(lots)

            serialized_lots = CarbureLotPublicSerializer(lots, many=True).data
            serialized_errors = GenericErrorSerializer(errors, many=True).data

            return SuccessResponse(
                {"lots": serialized_lots, "errors": serialized_errors, "total": len(serialized_lots)}
            )
    except:
        traceback.print_exc()
        return ErrorResponse(400, "ERROR")


# save the excel file on the server so we can open it later
def save_excel_file(excel_file, entity):
    now = datetime.datetime.now()
    directory = get_uploaded_files_directory()

    file_name = "%s_%s.xlsx" % (now.strftime("%Y%m%d.%H%M%S"), entity.name.upper())
    file_name = "".join((c for c in unicodedata.normalize("NFD", file_name) if unicodedata.category(c) != "Mn"))
    file_path = "%s/%s" % (directory, file_name)

    with open(file_path, "wb+") as destination:
        for chunk in excel_file.chunks():
            destination.write(chunk)

    return file_path


# parse the excel file and extract the relevant rows in a list
def parse_excel_file(file_path):
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.worksheets[0]

    data = []
    for row in sheet.rows:
        data.append([cell.value if isinstance(cell, openpyxl.cell.cell.Cell) else "" for cell in row])

    column_names = [str(col).strip().replace(' ', '_') for col in data[0]]
    data = data[1:]


    dataframe = pandas.DataFrame(data, columns=column_names)
    dataframe.fillna("", inplace=True)

    rows = []

    for row in dataframe.iterrows():
        row_data = row[1]

        # only keep rows where a quantity has been defined
        has_quantity = row_data.get("quantity", "") != ""
        has_volume = row_data.get("volume", "") != ""

        if has_quantity or has_volume:
            rows.append(row_data)

    return rows


# match old names given to columns to the latest ones
def backwards_compatibility(row):
    standardized = {
        "producer": row.get("producer"),
        "production_site": row.get("production_site"),
        "producer_certificate": row.get("producer_certificate") or row.get("production_site_reference"),
        "production_country": row.get("production_country") or row.get("production_site_country"),
        "production_site_commissioning_date": row.get("production_site_commissioning_date"),
        "double_counting_certificate": row.get("double_counting_certificate") or row.get("double_counting_registration"),  # fmt:skip
        "document_reference": row.get("document_reference") or row.get("dae") or row.get("transport_document_reference"),  # fmt:skip
        "delivery_type": row.get("delivery_type"),
        "supplier": row.get("supplier"),
        "supplier_certificate": row.get("supplier_certificate"),
        "middleman_certificate": row.get("middleman_certificate") or row.get("vendor_certificate"),
        "client": row.get("client"),
        "delivery_date": row.get("delivery_date"),
        "delivery_site": row.get("delivery_site"),
        "delivery_country": row.get("delivery_country") or row.get("delivery_site_country"),
        "biofuel": row.get("biofuel") or row.get("biocarburant_code"),
        "feedstock": row.get("feedstock") or row.get("matiere_premiere_code"),
        "country_of_origin": row.get("country_of_origin") or row.get("pays_origine_code"),
        "quantity": row.get("quantity") or row.get("volume"),
        "quantity_unit": row.get("quantity_unit", CarbureUnit.LITER),
        "eec": row.get("eec"),
        "el": row.get("el"),
        "ep": row.get("ep"),
        "etd": row.get("etd"),
        "eu": row.get("eu"),
        "esca": row.get("esca"),
        "eccs": row.get("eccs"),
        "eccr": row.get("eccr"),
        "eee": row.get("eee"),
        "free_field": row.get("free_field") or row.get("champ_libre"),
    }

    if str(row.get("mac")).strip() == "1":
        standardized["delivery_type"] = CarbureLot.RFC

    return standardized

def parse_fields(row):
    parser = FieldParser(row)
    return {
        "producer": parser.get_str("producer"),
        "production_site": parser.get_str("production_site"),
        "producer_certificate": parser.get_str("producer_certificate"),
        "production_country": parser.get_str("production_country"),
        "production_site_commissioning_date": parser.get_date("production_site_commissioning_date"),
        "double_counting_certificate": parser.get_str("double_counting_certificate"),
        "document_reference": parser.get_str("document_reference"),
        "free_field": parser.get_str("free_field"),
        "delivery_type": parser.get_str("delivery_type"),
        "supplier": parser.get_str("supplier"),
        "supplier_certificate": parser.get_str("supplier_certificate"),
        "middleman_certificate": parser.get_str("middleman_certificate"),
        "client": parser.get_str("client"),
        "delivery_date": parser.get_date("delivery_date"),
        "delivery_site": parser.get_str("delivery_site"),
        "delivery_country": parser.get_str("delivery_country"),
        "biofuel": parser.get_str("biofuel"),
        "feedstock": parser.get_str("feedstock"),
        "country_of_origin": parser.get_str("country_of_origin"),
        "quantity": parser.get_float("quantity"),
        "quantity_unit": parser.get_str("quantity_unit"),
        "eec": parser.get_float("eec"),
        "el": parser.get_float("el"),
        "ep": parser.get_float("ep"),
        "etd": parser.get_float("etd"),
        "eu": parser.get_float("eu"),
        "esca": parser.get_float("esca"),
        "eccs": parser.get_float("eccs"),
        "eccr": parser.get_float("eccr"),
        "eee": parser.get_float("eee"),
    }


# create lot rows in the database for all the data given
def create_lots(rows, entity):
    lots = []
    for row in rows:
        delivery_date = row.get("delivery_date")
        period = delivery_date.year * 100 + delivery_date.month
        year = delivery_date.year

        lot = CarbureLot(
            added_by=entity,
            period=period,
            year=year,
            # production data
            carbure_producer=row.get("carbure_producer"),
            unknown_producer=row.get("unknown_producer"),
            carbure_production_site=row.get("carbure_production_site"),
            unknown_production_site=row.get("unknown_production_site"),
            production_country=row.get("production_country"),
            production_site_commissioning_date=row.get("production_site_commissioning_date"),
            production_site_certificate=row.get("producer_certificate"),
            production_site_double_counting_certificate=row.get("double_counting_certificate"),
            # supplier data
            carbure_supplier=row.get("carbure_supplier"),
            unknown_supplier=row.get("unknown_supplier"),
            supplier_certificate=row.get("supplier_certificate"),
            carbure_vendor=row.get("carbure_middleman"),
            vendor_certificate=row.get("middleman_certificate"),
            # delivery
            transport_document_reference=row.get("document_reference"),
            carbure_client=row.get("carbure_client"),
            unknown_client=row.get("unknown_client"),
            delivery_date=row.get("delivery_date"),
            carbure_delivery_site=row.get("carbure_delivery_site"),
            unknown_delivery_site=row.get("unknown_delivery_site"),
            delivery_site_country=row.get("delivery_country"),
            delivery_type=row.get("delivery_type"),
            # lot details
            feedstock=row.get("feedstock"),
            biofuel=row.get("biofuel"),
            country_of_origin=row.get("country_of_origin"),
            free_field=row.get("free_field"),
            # GHG values
            eec=row.get("eec"),
            el=row.get("el"),
            ep=row.get("ep"),
            etd=row.get("etd"),
            eu=row.get("eu"),
            esca=row.get("esca"),
            eccs=row.get("eccs"),
            eccr=row.get("eccr"),
            eee=row.get("eee"),
        )

        lot.update_ghg()
        update_lot_quantities(lot, row)
        lots.append(lot)

    CarbureLot.objects.bulk_create(lots, batch_size=100)

    return (
        CarbureLot.objects.select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_production_site",
            "carbure_production_site__producer",
            "carbure_production_site__country",
            "production_country",
            "carbure_dispatch_site",
            "carbure_dispatch_site__country",
            "dispatch_site_country",
            "carbure_delivery_site",
            "carbure_delivery_site__country",
            "delivery_site_country",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "parent_lot",
            "parent_stock",
            "parent_stock__carbure_client",
            "parent_stock__carbure_supplier",
            "parent_stock__feedstock",
            "parent_stock__biofuel",
            "parent_stock__depot",
            "parent_stock__country_of_origin",
            "parent_stock__production_country",
        )
        .prefetch_related(
            "genericerror_set",
            "carbure_production_site__productionsitecertificate_set",
            "carbure_production_site__productionsiteinput_set",
            "carbure_production_site__productionsiteoutput_set",
        )
        .filter(added_by=entity)
        .order_by("-id")[0 : len(lots)]
    )


# loops through rows and add missing data inferable from current entity
def fill_defaults(row, entity):
    defaults = {**row}

    # if the feedstock is not DC, empty the certificate field
    is_double_counting = defaults.get("feedstock") and defaults.get("feedstock").is_double_compte
    if not is_double_counting:
        defaults["double_counting_certificate"] = None

    # no producer is defined => current entity is the producer
    if entity.entity_type == Entity.PRODUCER:
        if not defaults.get("carbure_producer") and not defaults.get("unknown_producer"):
            defaults["carbure_producer"] = entity

        if defaults.get("carbure_producer") == entity:
            if not defaults.get("supplier_certificate"):
                defaults["supplier_certificate"] = defaults["producer_certificate"]

    # no supplier is defined and entity is not client => current entity is the supplier
    is_client = defaults.get("carbure_client") == entity
    if not is_client and not defaults.get("carbure_supplier") and not defaults.get("unknown_supplier"):
        defaults["carbure_supplier"] = entity

    # entity is supplier and no supplier certificate is defined => use default certificate
    if defaults.get("carbure_supplier") == entity:
        if not defaults.get("supplier_certificate"):
            defaults["supplier_certificate"] = entity.default_certificate

    # no client is defined and entity is not supplier => current entity is the client
    if entity.entity_type == Entity.OPERATOR:
        is_supplier = defaults.get("carbure_supplier") == entity
        if not is_supplier and not defaults.get("carbure_client") and not defaults.get("unknown_client"):
            defaults["carbure_client"] = entity

        if defaults.get("delivery_type") == CarbureLot.UNKNOWN:
            defaults["delivery_type"] = CarbureLot.BLENDING


    # entity is neither supplier nor client => the current entity is a middleman in the transaction
    is_middleman = defaults.get("carbure_supplier") != entity and defaults.get("carbure_client") != entity
    if is_middleman:
        defaults["carbure_middleman"] = entity
        if not defaults.get("middleman_certificate"):
            defaults["middleman_certificate"] = entity.default_certificate

    # if entity is not middleman => remove any middleman certificate
    if not is_middleman:
        defaults["middleman_certificate"] = None

    # if production site is known and production country is not set => use the depot country
    if defaults.get('carbure_production_site'):
        production_site = defaults.get("carbure_production_site")
        defaults["production_country"] = production_site.country
        defaults["production_site_commissioning_date"] = production_site.date_mise_en_service
        if is_double_counting:
            defaults["double_counting_certificate"] = production_site.dc_reference

    # if depot is known and delivery country is not set => use the depot country
    if defaults.get('carbure_delivery_site'):
        defaults["delivery_country"] = defaults.get("carbure_delivery_site").country

    # if the delivery is made outside of france => make it an export by default
    is_delivered_in_fr = defaults.get("delivery_country") and defaults.get("delivery_country").code_pays == "FR"
    if defaults.get("delivery_type") == CarbureLot.UNKNOWN and not is_delivered_in_fr:
        defaults["delivery_type"] = CarbureLot.EXPORT

    return defaults


# checks the different columns of the given rows and match them using carbure data
def enrich_data(rows, entity):
    enriched_rows = []

    finder = FuzzyFinder()

    for row in rows:
        enriched = {}

        # - MATCH GENERAL LOT COLUMNS:

        enriched["document_reference"] = row.get("document_reference")
        enriched["free_field"] = row.get("free_field")
        enriched["quantity"] = row.get("quantity")
        enriched["quantity_unit"] = row.get("quantity_unit")

        enriched["biofuel"] = finder.find_biofuel(row.get("biofuel"))
        enriched["feedstock"] = finder.find_feedstock(row.get("feedstock"))
        enriched["country_of_origin"] = finder.find_country(row.get("country_of_origin"))

        # - MATCH PRODUCTION COLUMNS:
        producer = finder.find_entity(row.get("producer"), Entity.PRODUCER)
        if producer:
            enriched["carbure_producer"] = producer
            enriched["unknown_producer"] = None
        else:
            enriched["carbure_producer"] = None
            enriched["unknown_producer"] = row.get("producer")

        production_site = finder.find_production_site(row.get("production_site"), entity)
        if production_site:
            enriched["carbure_production_site"] = production_site
            enriched["unknown_production_site"] = None
        else:
            enriched["carbure_production_site"] = None
            enriched["unknown_production_site"] = row.get("production_site")

        enriched["production_country"] = finder.find_country(row.get("production_country"))

        enriched["producer_certificate"] = finder.find_certificate(row.get("producer_certificate"))
        enriched["production_site_commissioning_date"] = row.get("production_site_commissioning_date")
        enriched["double_counting_certificate"] = row.get("double_counting_certificate")

        # - MATCH DELIVERY COLUMNS:

        supplier = finder.find_entity(row.get("supplier"))
        if supplier:
            enriched["carbure_supplier"] = supplier
            enriched["unknown_supplier"] = None
        else:
            enriched["carbure_supplier"] = None
            enriched["unknown_supplier"] = row.get("supplier")

        enriched["supplier_certificate"] = finder.find_certificate(row.get("supplier_certificate"))
        enriched["middleman_certificate"] = finder.find_certificate(row.get("middleman_certificate"))

        client = finder.find_entity(row.get("client"))
        if client:
            enriched["carbure_client"] = client
            enriched["unknown_client"] = None
        else:
            enriched["carbure_client"] = None
            enriched["unknown_client"] = row.get("client")

        delivery_type = row.get("delivery_type")
        delivery_types = (CarbureLot.RFC, CarbureLot.TRADING, CarbureLot.STOCK, CarbureLot.BLENDING, CarbureLot.EXPORT, CarbureLot.PROCESSING, CarbureLot.DIRECT)
        enriched["delivery_type"] = delivery_type if delivery_type in delivery_types else CarbureLot.UNKNOWN

        enriched["delivery_date"] = row.get("delivery_date")

        delivery_site = finder.find_depot(row.get("delivery_site"))
        if delivery_site:
            enriched["carbure_delivery_site"] = delivery_site
            enriched["unknown_delivery_site"] = None
        else:
            enriched["carbure_delivery_site"] = None
            enriched["unknown_delivery_site"] = row.get("delivery_site")

        enriched["delivery_country"] = finder.find_country(row.get("delivery_country"))

        # - MATCH GHG COLUMNS

        enriched["eec"] = row.get("eec")
        enriched["el"] = row.get("el")
        enriched["ep"] = row.get("ep")
        enriched["etd"] = row.get("etd")
        enriched["eu"] = row.get("eu")
        enriched["esca"] = row.get("esca")
        enriched["eccs"] = row.get("eccs")
        enriched["eccr"] = row.get("eccr")
        enriched["eee"] = row.get("eee")

        enriched_rows.append(enriched)

    return enriched_rows


def update_lot_quantities(lot, data):
    volume = None
    weight = None
    lhv_amount = None

    quantity = round(float(data.get("quantity")), 2)
    unit = data.get("quantity_unit", CarbureUnit.LITER).lower()

    if unit == CarbureUnit.LITER:
        volume = quantity
        weight = round(volume * lot.biofuel.masse_volumique, 2)
        lhv_amount = round(volume * lot.biofuel.pci_litre, 2)
    elif unit == CarbureUnit.KILOGRAM:
        weight = quantity
        volume = round(weight / lot.biofuel.masse_volumique, 2)
        lhv_amount = round(volume * lot.biofuel.pci_litre, 2)
    elif unit == CarbureUnit.LHV:
        lhv_amount = quantity
        volume = round(lhv_amount / lot.biofuel.pci_litre, 2)
        weight = round(volume * lot.biofuel.masse_volumique, 2)

    lot.volume = volume
    lot.weight = weight
    lot.lhv_amount = lhv_amount


class FuzzyFinder:
    def __init__(self):
        lastyear = datetime.date.today() - datetime.timedelta(days=365)
        self.entities = list(Entity.objects.all())
        self.biofuels = list(Biocarburant.objects.all())
        self.feedstocks = list(MatierePremiere.objects.all())
        self.production_sites = list(ProductionSite.objects.all())
        self.depots = list(Depot.objects.all())
        self.countries = list(Pays.objects.all())
        self.certificates = list(GenericCertificate.objects.filter(valid_until__gte=lastyear))

    def find_entity(self, name, type=None):
        entities = [entity for entity in self.entities if not type or entity.entity_type == type]
        return self.find(name, entities, "name", 0.7)

    def find_biofuel(self, name_or_code):
        found_code = self.find(name_or_code, self.biofuels, "code", 0.9)
        found_name = self.find(name_or_code, self.biofuels, "name", 0.8)
        return found_code or found_name

    def find_feedstock(self, name_or_code):
        found_code = self.find(name_or_code, self.feedstocks, "code", 0.9)
        found_name = self.find(name_or_code, self.feedstocks, "name", 0.8)
        return found_code or found_name

    def find_production_site(self, name_or_code, producer):
        production_sites = [prod_site for prod_site in self.production_sites if prod_site.producer == producer]
        return self.find(name_or_code, production_sites, "name", 0.7)

    def find_depot(self, name_or_code):
        depot_code = self.find(name_or_code, self.depots, "depot_id", 1)
        depot_name = self.find(name_or_code, self.depots, "name", 0.7)
        return depot_code or depot_name

    def find_country(self, name_or_code):
        country_code = self.find(name_or_code, self.countries, "code_pays", 1)
        country_name = self.find(name_or_code, self.countries, "name", 0.7)
        return country_code or country_name

    def find_certificate(self, certificate_id):
        if not certificate_id:
            return None
        certificates = [cert.certificate_id for cert in self.certificates if certificate_id in cert.certificate_id]
        return certificates[0] if len(certificates) > 0 else None

    def find(self, input, rows, column, cutoff):
        values = [str(getattr(row, column)).lower() for row in rows]
        matched_values = difflib.get_close_matches(str(input).lower(), values, 1, cutoff)

        if len(matched_values) > 0:
            matched_rows = [row for row in rows if str(getattr(row, column)).lower() == matched_values[0]]
            if len(matched_rows) > 0:
                return matched_rows[0]


def trim_zero(value):
    try:
        return str(int(value))
    except:
        return str(value)

class FieldParser:
    def __init__(self, dict):
        self.dict = dict

    def get(self, field):
        value = self.dict.get(field)
        return str(trim_zero(value)).strip() if value else None

    def get_str(self, field):
        try:
            return self.get(field) or ""
        except:
            return ""

    def get_int(self, field):
        try:
            return int(self.get(field)) or 0
        except:
            return 0

    def get_float(self, field):
        try:
            return float(self.get(field)) or 0.0
        except:
            return 0.0

    def get_bool(self, field):
        try:
            return bool(self.get(field)) or False
        except:
            return False

    def get_date(self, field):
        try:
            value = self.get(field)

            if value == "":
                return None
            if value is None:
                return value
            if isinstance(value, int):
                return datetime.datetime.fromordinal(datetime.datetime(1900, 1, 1).toordinal() + value - 2)
            if isinstance(value, datetime.datetime):
                return value.date()
            if isinstance(value, datetime.date):
                return value

            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except Exception:
                pass

            try:
                return datetime.datetime.strptime(value, "%d/%m/%Y").date()
            except Exception:
                pass

            try:
                return datetime.datetime.strptime(value, "%d/%m/%y").date()
            except Exception:
                pass

            return dateutil.parser.parse(value, dayfirst=True).date()
        except:
            return None


[
    "producer",
    "production_site",
    "producer_certificate",
    "production_country",
    "production_site_commissioning_date",
    "double_counting_certificate",
    "document_reference",
    "delivery_type",
    "supplier",
    "supplier_certificate",
    "middleman_certificate",
    "client",
    "delivery_date",
    "delivery_site",
    "delivery_country",
    "biofuel",
    "feedstock",
    "country_of_origin",
    "quantity",
    "quantity_unit",
    "eec",
    "el",
    "ep",
    "etd",
    "eu",
    "esca",
    "eccs",
    "eccr",
    "eee",
    "free_field",
    "internal_id",
]
