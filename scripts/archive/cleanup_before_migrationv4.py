# Generated by Django 3.2.8 on 2021-11-05 14:29

from django.db import migrations
import datetime
import calendar
from django.db.models.aggregates import Sum
import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import connection

from core.models import AdminTransactionComment, CarbureLot, CarbureLotComment, CarbureLotEvent, CarbureStock, CarbureStockTransformation, ETBETransformation, Entity, GenericError, LotTransaction, LotV2, TransactionComment, TransactionUpdateHistory

def cleanup_tables():
    cursor = connection.cursor()
    sql1 = "SET FOREIGN_KEY_CHECKS = 0;"
    cursor.execute(sql1)
    sql2 = "DROP TABLE IF EXISTS carbure_certificates, carbure_entity_certificates, carbure_lots, carbure_lots_comments, carbure_lots_events, carbure_notifications, carbure_stock, carbure_stock_events, carbure_stock_transformations;"
    cursor.execute(sql2)
    sql3 = "SET FOREIGN_KEY_CHECKS = 1;"
    cursor.execute(sql3)
    # delete ghost lots
    cursor.execute("delete from lots_v2 where id in (select id from lots_v2 where id not in (select lot_id from transactions))")
   

if __name__ == '__main__':
    cleanup_tables()
