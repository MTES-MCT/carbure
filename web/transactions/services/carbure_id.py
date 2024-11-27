from django.db.models import CharField, F, QuerySet, Value
from django.db.models.functions import Coalesce, Concat

from core.models import CarbureLot, CarbureStock


def bulk_generate_lot_carbure_id(lots: QuerySet[CarbureLot], save=False):
    lots_with_new_id = (
        lots.select_related("carbure_delivery_site", "production_country")
        .annotate(
            country_code=Coalesce("production_country__code_pays", Value("00"), output_field=CharField()),
            delivery_site_id=Coalesce("carbure_delivery_site__customs_id", Value("00"), output_field=CharField()),
            new_carbure_id=Concat(
                Value("L"),
                F("period"),
                Value("-"),
                F("country_code"),
                Value("-"),
                F("delivery_site_id"),
                Value("-"),
                F("id"),
                output_field=CharField(),
            ),
        )
        .exclude(carbure_id=F("new_carbure_id"))
    )

    if save:
        lots_to_update = []
        for lot in lots_with_new_id:
            lot.carbure_id = lot.new_carbure_id
            lots_to_update.append(lot)
        CarbureLot.objects.bulk_update(lots_to_update, ["carbure_id"])

    return lots_with_new_id


def bulk_generate_stock_carbure_id(stocks: QuerySet[CarbureStock], save=False):
    stocks_with_new_id = (
        stocks.select_related("parent_lot", "parent_transformation__source_stock__parent_lot", "production_country", "depot")
        .annotate(
            country_code=Coalesce("production_country__code_pays", Value("00"), output_field=CharField()),
            delivery_site_id=Coalesce("depot__customs_id", Value("00"), output_field=CharField()),
            parent_lot_period=F("parent_lot__period"),
            parent_transform_period=F("parent_transformation__source_stock__parent_lot__period"),
            period=Coalesce("parent_lot_period", "parent_transform_period", Value("000000"), output_field=CharField()),
            new_carbure_id=Concat(
                Value("S"),
                F("period"),
                Value("-"),
                F("country_code"),
                Value("-"),
                F("delivery_site_id"),
                Value("-"),
                F("id"),
                output_field=CharField(),
            ),
        )
        .exclude(carbure_id=F("new_carbure_id"))
    )

    if save:
        stocks_to_update = []
        for stock in stocks_with_new_id:
            stock.carbure_id = stock.new_carbure_id
            stocks_to_update.append(stock)
        CarbureStock.objects.bulk_update(stocks_to_update, ["carbure_id"])

    return stocks_with_new_id
