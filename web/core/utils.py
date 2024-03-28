import os
import unicodedata
from django import forms
from django.db import connection, transaction
from django.conf import settings
from django.core.paginator import Paginator
import xlsxwriter
from core.xlsx_v3 import make_carbure_lots_sheet
from core.models import Entity, UserRights
from os import environ as env


# transform a string into a standard form in lower case without accents
def normalize_string(input_str: str):
    lower_case = (input_str or "").strip().lower()
    nfkd_form = unicodedata.normalize("NFKD", lower_case)
    only_ascii = nfkd_form.encode("ASCII", "ignore")
    return only_ascii


@transaction.atomic
def bulk_update_or_create(Model, id_field, rows, batch=1000):
    if len(rows) == 0:
        return

    paginator = Paginator(rows, batch)

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        page_rows = page.object_list

        row_ids = [row[id_field] for row in rows]
        update_keys = [key for key in rows[0].keys() if key != id_field]

        # first get the list of existing objects matching the given rows
        id__in = "%s__in" % id_field
        existing_objects_dict = {getattr(obj, id_field): obj for obj in Model.objects.filter(**{id__in: row_ids})}
        existing_ids = existing_objects_dict.keys()

        existing_objects = []
        new_objects = []

        for row in page_rows:
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

        Model.objects.bulk_update(existing_objects, update_keys)
        Model.objects.bulk_create(new_objects)

    return existing_objects, new_objects


def generate_reports(name, entity_lots, include_partners=False):
    os.makedirs("/tmp/reports", exist_ok=True)

    lots_by_entity = {}

    for lot in entity_lots:
        added_by = lot.added_by_id if lot.added_by else None
        carbure_supplier = lot.carbure_supplier_id if lot.carbure_supplier else None
        carbure_client = lot.carbure_client_id if lot.carbure_client else None

        if added_by is not None:
            if added_by not in lots_by_entity:
                lots_by_entity[added_by] = {}
            lots_by_entity[added_by][lot.id] = lot

        if include_partners:
            if carbure_supplier is not None:
                if carbure_supplier not in lots_by_entity:
                    lots_by_entity[carbure_supplier] = {}
                lots_by_entity[carbure_supplier][lot.id] = lot

            if carbure_client is not None:
                if carbure_client not in lots_by_entity:
                    lots_by_entity[carbure_client] = {}
                lots_by_entity[carbure_client][lot.id] = lot

    print("> Impacted entities: %d" % len(lots_by_entity))

    entities = Entity.objects.filter(id__in=list(lots_by_entity))
    entities_by_id = {entity.id: entity for entity in entities}

    users_by_entity = get_entities_users(entities)

    for entity_id in lots_by_entity:
        entity = entities_by_id[entity_id]
        location = f"/tmp/reports/{name}_{entity.name}.xlsx"
        entity_lots = sorted(lots_by_entity[entity_id].values(), key=lambda l: l.delivery_date)
        entity_users = users_by_entity.get(entity_id, [])
        emails = ", ".join([user.email for user in entity_users])
        print(f"> {len(entity_lots)} lots for {entity.name} ({emails})")
        workbook = xlsxwriter.Workbook(location)
        make_carbure_lots_sheet(workbook, entity, entity_lots)
        workbook.close()


def get_entities_users(entities):
    users_by_entity = {}
    user_rights_by_entity = {}
    user_rights = UserRights.objects.filter(entity__in=entities, user__is_staff=False)

    for user_right in user_rights:
        if user_right.entity_id not in user_rights_by_entity:
            user_rights_by_entity[user_right.entity_id] = []
        user_rights_by_entity[user_right.entity_id].append(user_right)

    for entity_id in user_rights_by_entity:
        user_rights = user_rights_by_entity[entity_id]
        admins = [user_right.user for user_right in user_rights if user_right.role == UserRights.ADMIN]
        users = [user_right.user for user_right in user_rights if user_right.role == UserRights.RW]
        users_by_entity[entity_id] = admins if len(admins) > 0 else users

    return users_by_entity


def run_query(query_path, *args):
    """Read a query SQL from a file and run it on the database"""

    full_query_path = os.path.join(settings.BASE_DIR, query_path)
    with open(full_query_path, "r", encoding="utf-8") as query_file:
        query_sql = query_file.read().replace("\n", " ").replace("--", "")
        query_sql = " ".join(query_sql.split())

        with connection.cursor() as cursor:
            # recursively query for the whole family trees for the given lot ids
            cursor.execute(query_sql, args)
            # grab the list of results in the form of an array of tuples
            return cursor.fetchall()


# combine many lists in a single one where all items are defined, unique, and ordered
def combine(*lists):
    combined_list = set()
    for list in lists:
        combined_list.update(list)
    return sorted([item for item in combined_list if item or item == 0])


class MultipleValueField(forms.TypedMultipleChoiceField):
    # def __init__(self, *args, **kwargs):
    #     super(MultipleValueField, self).__init__(*args, **kwargs)
    def valid_value(self, value):
        return True


class Validator(forms.Form):
    INVALID_DATA = "INVALID_DATA"

    # potential date formats inside the excel file
    DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"]

    @classmethod
    def bulk_validate(SpecializedValidator, items, context) -> tuple[list, list]:
        """
        Use this method to validate a list of dicts with the current Validator.
        Ex: If you defined a LotValidator, you can run `valid_lots, errors = LotValidator.bulk_validate(list_of_lot_data, context)`
        """

        valid_items = []
        errors = []

        for item_data in items:
            form = SpecializedValidator(item_data, context=context)
            if form.is_valid():
                valid_items.append(form.cleaned_data)
            else:
                errors.append({"error": Validator.INVALID_DATA, "line": item_data.get("line"), "meta": form.errors})

        return valid_items, errors

    # extend the default Form constructor by adding the ability to set a context with external data
    # useful during calls to self.extend() and self.validate() as you can use data that doesn't belong to the FormData itself
    def __init__(self, data, context={}, **kwargs):
        super().__init__(data=data, **kwargs)
        self.context = context
        extended_data = self.extend(self.data)
        self.data.update(extended_data)

    # dynamically set data inside the source object before cleaning data and validation
    def extend(self, data):
        return data

    # validate the cleaned data created by django's Form
    # useful to do checks across all fields or use external resources
    def validate(self, data):
        pass

    # extend the default clean method to run the validate method before returning the cleaned data
    def clean(self):
        cleaned_data = super().clean()
        self.validate(cleaned_data)
        return cleaned_data


class CarbureEnv:
    is_prod = True if env.get("IMAGE_TAG") == "prod" else False
    is_staging = True if env.get("IMAGE_TAG") == "staging" else False
    is_local = True if env.get("IMAGE_TAG") == "local" else False
    is_dev = True if env.get("IMAGE_TAG") == "dev" else False
