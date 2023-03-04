import os
import unicodedata
from django.db import transaction
import xlsxwriter
from core.xlsx_v3 import make_carbure_lots_sheet


# transform a string into a standard form in lower case without accents
def normalize_string(input_str: str):
    lower_case = (input_str or "").strip().lower()
    nfkd_form = unicodedata.normalize("NFKD", lower_case)
    only_ascii = nfkd_form.encode("ASCII", "ignore")
    return only_ascii


@transaction.atomic
def bulk_update_or_create(Model, id_field, rows):
    if len(rows) == 0:
        return

    row_ids = [row[id_field] for row in rows]
    update_keys = [key for key in rows[0].keys() if key != id_field]

    # first get the list of existing objects matching the given rows
    id__in = "%s__in" % id_field
    existing_objects_dict = {getattr(obj, id_field): obj for obj in Model.objects.filter(**{id__in: row_ids})}
    existing_ids = existing_objects_dict.keys()

    existing_objects = []
    new_objects = []

    for row in rows:
        id = row[id_field]
        if id in existing_ids:
            existing = existing_objects_dict[id]
            # update the existing models with the new data, but without saving yet
            for key in row:
                setattr(existing, key, row[key])
            # put is aside in order to update everything all at once later
            existing_objects.append(existing)
        else:
            # create a new model instance and save it to bulk_create later
            new = Model(**row)
            new_objects.append(new)

    Model.objects.bulk_update(existing_objects, update_keys, 1000)
    Model.objects.bulk_create(new_objects, 1000)

    return existing_objects, new_objects


def generate_reports(name, entity_lots):
    os.makedirs("/tmp/reports", exist_ok=True)

    lots_by_entity = {}

    for lot in entity_lots:
        added_by = lot.added_by.name if lot.added_by else None
        carbure_supplier = lot.carbure_supplier.name if lot.carbure_supplier else None
        carbure_client = lot.carbure_client.name if lot.carbure_client else None

        if added_by is not None:
            if added_by not in lots_by_entity:
                lots_by_entity[added_by] = {}
            lots_by_entity[added_by][lot.id] = lot

        if carbure_supplier is not None:
            if carbure_supplier not in lots_by_entity:
                lots_by_entity[carbure_supplier] = {}
            lots_by_entity[carbure_supplier][lot.id] = lot

        if carbure_client is not None:
            if carbure_client not in lots_by_entity:
                lots_by_entity[carbure_client] = {}
            lots_by_entity[carbure_client][lot.id] = lot

    print("> Impacted entities: %d" % len(lots_by_entity))

    for entity in lots_by_entity:
        location = "/tmp/reports/%s_%s.xlsx" % (name, entity)
        entity_lots = sorted(lots_by_entity[entity].values(), key=lambda l: l.delivery_date)
        print("> %d lots for %s: '%s'" % (len(entity_lots), entity, location))
        workbook = xlsxwriter.Workbook(location)
        make_carbure_lots_sheet(workbook, None, entity_lots)
        workbook.close()
