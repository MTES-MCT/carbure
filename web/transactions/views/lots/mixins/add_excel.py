import datetime
import unicodedata

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_scoring
from core.common import convert_template_row_to_formdata, get_uploaded_files_directory
from core.models import CarbureLotEvent, CarbureStockEvent, Entity
from transactions.helpers import bulk_insert_lots, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data


class AddExcelMixin:
    @action(methods=["post"], detail=False, url_path="add-excel")
    def add_excel(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(pk=entity_id)
        d = get_prefetched_data(entity)

        f = request.FILES.get("file")
        if f is None:
            return ValidationError({"message": "Missing File"})

        # save file
        directory = get_uploaded_files_directory()
        now = datetime.datetime.now()
        filename = "%s_%s.xlsx" % (now.strftime("%Y%m%d.%H%M%S"), entity.name.upper())
        filename = "".join((c for c in unicodedata.normalize("NFD", filename) if unicodedata.category(c) != "Mn"))
        filepath = "%s/%s" % (directory, filename)
        with open(filepath, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        data = convert_template_row_to_formdata(entity, d, filepath)
        nb_total = 0
        nb_valid = 0
        nb_invalid = 0
        lots = []
        lots_errors = []

        with transaction.atomic():
            for row in data:
                lot_obj, errors = construct_carbure_lot(d, entity, row)
                if not lot_obj:
                    nb_invalid += 1
                else:
                    nb_valid += 1
                nb_total += 1
                lots.append(lot_obj)
                lots_errors.append(errors)
            lots_created = bulk_insert_lots(entity, lots, lots_errors, d)
            if len(lots_created) == 0:
                raise APIException({"message": "Something went wrong"})

            background_bulk_scoring(lots_created)
            for lot in lots_created:
                e = CarbureLotEvent()
                e.event_type = CarbureLotEvent.CREATED
                e.lot_id = lot.id
                e.user = request.user
                e.metadata = {"source": "EXCEL"}
                e.save()
                if lot.parent_stock:
                    event = CarbureStockEvent()
                    event.event_type = CarbureStockEvent.SPLIT
                    event.stock = lot.parent_stock
                    event.user = request.user
                    event.metadata = {
                        "message": "Envoi lot.",
                        "volume_to_deduct": lot.volume,
                    }
                    event.save()

        return Response(
            {"lots": nb_total, "valid": nb_valid, "invalid": nb_invalid},
            status=status.HTTP_200_OK,
        )
