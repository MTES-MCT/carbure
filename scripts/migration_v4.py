# Generated by Django 3.2.8 on 2021-11-05 14:29

from django.core.paginator import Paginator
from django.db import migrations
import datetime
import calendar
from django.db.models.aggregates import Sum
import os
import django
import argparse
from tqdm import tqdm
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import connection

from core.models import *
from certificates.models import *

# map old id to new id
TX_ID_MIGRATED = {}
   
def create_new_tx_and_child(tx):
    if tx.id in TX_ID_MIGRATED:
        # ignore, this is a child tx already migrated
        new_id = TX_ID_MIGRATED[tx.id]
        if new_id:
            return CarbureLot.objects.get(id=TX_ID_MIGRATED[tx.id])
        else:
            return None
    lot = CarbureLot()
    delivery_date = tx.delivery_date or datetime.datetime.today()
    lot.period = delivery_date.year * 100 + delivery_date.month
    lot.year = delivery_date.year
    lot.carbure_id = tx.lot.carbure_id
    lot.carbure_producer = tx.lot.carbure_producer
    lot.unknown_producer = tx.lot.unknown_producer
    lot.carbure_production_site = tx.lot.carbure_production_site
    lot.unknown_production_site = tx.lot.unknown_production_site
    lot.production_country = tx.lot.carbure_production_site.country if tx.lot.carbure_production_site else tx.lot.unknown_production_country
    lot.production_site_commissioning_date = tx.lot.carbure_production_site.date_mise_en_service if tx.lot.carbure_production_site else tx.lot.unknown_production_site_com_date
    lot.production_site_certificate = tx.lot.carbure_production_site_reference if tx.lot.carbure_production_site else tx.lot.unknown_production_site_reference
    lot.production_site_certificate_type = None
    lot.production_site_double_counting_certificate = tx.lot.carbure_production_site.dc_reference if tx.lot.carbure_production_site else tx.lot.unknown_production_site_dbl_counting

    lot.transport_document_type = lot.OTHER
    lot.transport_document_reference = tx.dae
    lot.carbure_client = tx.carbure_client
    lot.unknown_client = tx.unknown_client
    lot.dispatch_date = None
    lot.carbure_dispatch_site = None
    lot.unknown_dispatch_site = None
    lot.dispatch_site_country = None
    lot.delivery_date = delivery_date
    lot.carbure_delivery_site = tx.carbure_delivery_site
    lot.unknown_delivery_site = tx.unknown_delivery_site
    lot.delivery_site_country = tx.carbure_delivery_site.country if tx.carbure_delivery_site else tx.unknown_delivery_site_country

    if tx.lot.status == LotV2.DRAFT:
        lot.lot_status = CarbureLot.DRAFT
    else:
        lot.lot_status = CarbureLot.PENDING

    lot.correction_status = CarbureLot.NO_PROBLEMO
    if tx.delivery_status == LotTransaction.TOFIX:
        lot.correction_status = CarbureLot.IN_CORRECTION
    if tx.delivery_status == LotTransaction.FIXED:
        lot.correction_status = CarbureLot.FIXED

    if tx.delivery_status == LotTransaction.ACCEPTED:
        lot.lot_status = CarbureLot.ACCEPTED
    if tx.delivery_status == LotTransaction.FROZEN:
        lot.lot_status = CarbureLot.FROZEN
        lot.declared_by_client = True
        lot.declared_by_supplier = True

    lot.delivery_type = CarbureLot.BLENDING
    if tx.is_forwarded:
        if tx.carbure_client and tx.carbure_client.entity_type == Entity.OPERATOR:
            lot.delivery_type = CarbureLot.PROCESSING
        else:
            lot.delivery_type = CarbureLot.TRADING
    elif tx.is_mac:
        lot.delivery_type = CarbureLot.RFC
    elif tx.is_stock:
        lot.delivery_type = CarbureLot.STOCK
    elif tx.carbure_client and tx.carbure_client.entity_type in [Entity.TRADER, Entity.PRODUCER]:
        lot.delivery_type = CarbureLot.STOCK
    else:
        pass # default to blending
    lot.declared_by_supplier = False
    lot.declared_by_client = False
    lot.feedstock = tx.lot.matiere_premiere
    lot.biofuel = tx.lot.biocarburant
    lot.country_of_origin = tx.lot.pays_origine
    lot.volume = tx.lot.volume
    if lot.biofuel:
        lot.weight = lot.volume * lot.biofuel.masse_volumique
        lot.lhv_amount = lot.volume * lot.biofuel.pci_litre
    lot.eec = tx.lot.eec
    lot.el = tx.lot.el
    lot.ep = tx.lot.ep
    lot.etd = tx.lot.etd
    lot.eu = tx.lot.eu
    lot.esca = tx.lot.esca
    lot.eccs = tx.lot.eccs
    lot.eccr = tx.lot.eccr
    lot.eee = tx.lot.eee
    lot.ghg_total = tx.lot.ghg_total
    lot.ghg_reference = tx.lot.ghg_reference
    lot.ghg_reduction = tx.lot.ghg_reduction
    lot.ghg_reference_red_ii = tx.lot.ghg_reference_red_ii
    lot.ghg_reduction_red_ii = tx.lot.ghg_reduction_red_ii
    lot.added_by = tx.lot.added_by
    lot.parent_lot = None
    lot.parent_stock = None
    lot.free_field = tx.champ_libre
    lot.highlighted_by_admin = tx.highlighted_by_admin
    lot.highlighted_by_auditor = tx.highlighted_by_auditor

    if tx.lot.unknown_supplier != '':
        # create a first transaction from unknown supplier to tx.carbure_vendor
        # then one from tx.carbure_vendor to tx.carbure_client
        lot.unknown_supplier = tx.lot.unknown_supplier
        lot.supplier_certificate = tx.lot.unknown_supplier_certificate
        lot.supplier_certificate_type = None
        lot.save()
        first_tx_id = lot.id
        #creation_event = CarbureLotEvent()
        #creation_event.event_type = CarbureLotEvent.CREATED
        #creation_event.event_dt = tx.lot.added_time
        #creation_event.user = tx.lot.added_by_user
        #creation_event.lot_id = first_tx_id
        lot.pk = None
        lot.parent_lot_id = first_tx_id
    lot.carbure_supplier = tx.carbure_vendor
    lot.supplier_certificate = tx.carbure_vendor_certificate
    lot.supplier_certificate_type = None
    lot.save()
    #creation_event = CarbureLotEvent()
    #creation_event.event_type = CarbureLotEvent.CREATED
    #creation_event.event_dt = tx.lot.added_time
    #creation_event.user = tx.lot.added_by_user
    #creation_event.lot_id = lot.id
    TX_ID_MIGRATED[tx.id] = lot.id



    # for each TX
    # if is_stock, create stock, get child tx, link them to stock, check remaining volume
    if lot.delivery_type == CarbureLot.STOCK and lot.lot_status in [CarbureLot.ACCEPTED, CarbureLot.FROZEN]:
        # create CarbureStock instance
        stock = CarbureStock()
        stock.parent_lot = lot
        stock.parent_transformation = None
        stock.carbure_id = lot.carbure_id
        stock.depot = lot.carbure_delivery_site
        stock.carbure_client = lot.carbure_client
        stock.remaining_volume = tx.lot.remaining_volume
        stock.remaining_weight = tx.lot.remaining_volume * lot.biofuel.masse_volumique
        stock.remaining_lhv_amount = tx.lot.remaining_volume * lot.biofuel.pci_kg
        stock.feedstock = lot.feedstock
        stock.biofuel = lot.biofuel
        stock.country_of_origin = lot.country_of_origin
        stock.carbure_production_site = lot.carbure_production_site
        stock.unknown_production_site = lot.unknown_production_site
        stock.production_country = lot.production_country
        stock.carbure_supplier = lot.carbure_supplier
        stock.unknown_supplier = lot.unknown_supplier
        stock.ghg_reduction = lot.ghg_reduction
        stock.ghg_reduction_red_ii = lot.ghg_reduction_red_ii
        stock.save()
        stock_initial_volume = lot.volume

        if tx.lot.biocarburant.code == 'ETH':
            # check if I have been transformed into ETBE
            if ETBETransformation.objects.filter(previous_stock=tx.id).exists():
                transformations = ETBETransformation.objects.filter(previous_stock=tx.id)
                for trans in transformations:
                    # create new stock
                    child = trans.new_stock
                    if trans.new_stock.parent_tx is None:
                        trans.new_stock.parent_tx = tx
                        trans.new_stock.save()
                    etbe_stock = CarbureStock()
                    etbe_stock.parent_lot = None
                    etbe_stock.parent_transformation = None
                    etbe_stock.carbure_id = lot.carbure_id
                    etbe_stock.depot = lot.carbure_delivery_site
                    etbe_stock.carbure_client = lot.carbure_client
                    etbe_stock.remaining_volume = trans.volume_etbe
                    etbe_stock.remaining_weight = etbe_stock.remaining_volume * child.lot.biocarburant.masse_volumique
                    etbe_stock.remaining_lhv_amount = etbe_stock.remaining_volume * child.lot.biocarburant.pci_kg
                    etbe_stock.feedstock = child.lot.matiere_premiere
                    etbe_stock.biofuel = child.lot.biocarburant
                    etbe_stock.country_of_origin = child.lot.pays_origine
                    etbe_stock.carbure_production_site = child.lot.carbure_production_site
                    etbe_stock.unknown_production_site = child.lot.unknown_production_site
                    etbe_stock.production_country = child.lot.carbure_production_site.country if child.lot.carbure_production_site else child.lot.unknown_production_country
                    etbe_stock.carbure_supplier = child.carbure_vendor
                    etbe_stock.unknown_supplier = child.lot.unknown_supplier
                    etbe_stock.ghg_reduction = child.lot.ghg_reduction
                    etbe_stock.ghg_reduction_red_ii = child.lot.ghg_reduction_red_ii
                    etbe_stock.save()
                    # create transformation object
                    transformation = CarbureStockTransformation()
                    transformation.transformation_type = CarbureStockTransformation.ETH_ETBE
                    transformation.source_stock = stock
                    transformation.dest_stock = etbe_stock
                    transformation.volume_deducted_from_source = trans.volume_ethanol
                    transformation.volume_destination = trans.volume_etbe
                    transformation.metadata = {'volume_denaturant': trans.volume_denaturant, 'volume_etbe_eligible': trans.volume_etbe_eligible}
                    transformation.transformed_by = trans.added_by_user
                    transformation.entity = trans.added_by
                    transformation.transformation_dt = trans.added_time
                    transformation.save()

                    etbe_stock.parent_transformation = transformation
                    etbe_stock.save()
                    TX_ID_MIGRATED[child.id] = None
                    TX_ID_MIGRATED[trans.previous_stock.id] = None
                    # migrate child transactions
                    etbe_child = LotTransaction.objects.filter(parent_tx=trans.new_stock).exclude(carbure_client=trans.new_stock.carbure_client)
                    for c in etbe_child:
                        lot.pk = None
                        lot.carbure_supplier = stock.carbure_client
                        lot.carbure_client = c.carbure_client
                        lot.unknown_client = c.unknown_client
                        lot.delivery_type = CarbureLot.BLENDING
                        lot.parent_stock_id = etbe_stock.id
                        lot.transport_document_type = lot.OTHER
                        lot.transport_document_reference = c.dae
                        lot.carbure_client = c.carbure_client
                        lot.unknown_client = c.unknown_client
                        lot.dispatch_date = None
                        lot.carbure_dispatch_site = etbe_stock.depot
                        lot.unknown_dispatch_site = None
                        lot.dispatch_site_country = etbe_stock.depot.country if etbe_stock.depot else None
                        lot.delivery_date = c.delivery_date
                        lot.carbure_delivery_site = c.carbure_delivery_site
                        lot.unknown_delivery_site = c.unknown_delivery_site
                        lot.delivery_site_country = c.carbure_delivery_site.country if c.carbure_delivery_site else c.unknown_delivery_site_country
                        lot.volume = c.lot.volume
                        lot.biofuel = c.lot.biocarburant
                        #print('CHILD ETBE %d ADD %s %s %f to %s' % (c.id, lot.feedstock.name, lot.biofuel.name, lot.volume, lot.delivery_type))
                        lot.save()
                        TX_ID_MIGRATED[c.id] = lot.id


        # convert initial stock to ETBE
        stock_transformations = ETBETransformation.objects.filter(previous_stock=tx)
        #print('Stock transaction %d %s %d is transformed? %s' % (tx.id, tx.lot.biocarburant.name, tx.lot.volume, stock_transformations))
        #print('This stock has been transformed %d times' % (stock_transformations.count()))
        for t in stock_transformations:
            #print('Adjusting volume: remove ethanol %d, add etbe [%d]' % (t.volume_ethanol, t.volume_etbe))
            stock_initial_volume -= t.volume_ethanol
            stock_initial_volume += t.volume_etbe
            #TX_ID_MIGRATED[stock_transformations[0].previous_stock.id] = 0
            #TX_ID_MIGRATED[stock_transformations[0].new_stock.id] = 0

        #child = LotTransaction.objects.filter(parent_tx=tx, lot__biocarburant=tx.lot.biocarburant)
        child = LotTransaction.objects.filter(parent_tx=tx, lot__status='Validated')
        child_sum_volume = 0
        for c in child:
            child_sum_volume += c.lot.volume
            if c.id in TX_ID_MIGRATED:
                continue
            if c.lot.biocarburant.code == 'ETBE' and c.lot.parent_lot.biocarburant.code == 'ETH':
                transformation = ETBETransformation.objects.get(new_stock=c)
                child_sum_volume -= c.lot.volume
                child_sum_volume += transformation.volume_ethanol
                #print('parent: %d %s %f child %d %s %f of which ethanol %f' % (tx.id, tx.lot.biocarburant.name, tx.lot.volume, c.id, c.lot.biocarburant.name, c.lot.volume, transformation.volume_ethanol))
            #print('Child total accumulated sum %d' % (child_sum_volume))
            lot.pk = None # breaks the link with stock.parent_lot
            lot.carbure_supplier = stock.carbure_client
            lot.carbure_client = c.carbure_client
            lot.unknown_client = c.unknown_client
            lot.delivery_type = CarbureLot.BLENDING
            lot.parent_stock_id = stock.id
            lot.transport_document_type = lot.OTHER
            lot.transport_document_reference = c.dae
            lot.carbure_client = c.carbure_client
            lot.unknown_client = c.unknown_client
            lot.dispatch_date = None
            lot.carbure_dispatch_site = stock.depot
            lot.unknown_dispatch_site = None
            lot.dispatch_site_country = stock.depot.country if stock.depot else None
            lot.delivery_date = c.delivery_date
            lot.carbure_delivery_site = c.carbure_delivery_site
            lot.unknown_delivery_site = c.unknown_delivery_site
            lot.delivery_site_country = c.carbure_delivery_site.country if c.carbure_delivery_site else c.unknown_delivery_site_country
            lot.volume = c.lot.volume
            lot.biofuel = c.lot.biocarburant
            #print('CHILD ADD [tx id %d] %s %s %f to %s. Parent stock initial volume %d - remaining %d' % (c.id, lot.feedstock.name, lot.biofuel.name, lot.volume, lot.delivery_type, stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination, stock.remaining_volume))
            lot.save()
            #creation_event = CarbureLotEvent()
            #creation_event.event_type = CarbureLotEvent.CREATED
            #creation_event.event_dt = c.lot.added_time
            #creation_event.user = c.lot.added_by_user
            #creation_event.lot_id = lot.id
            TX_ID_MIGRATED[c.id] = lot.id

        theo_remaining = stock_initial_volume - child_sum_volume
        remaining = stock.remaining_volume
        diff = remaining - theo_remaining
        if abs(diff) > 0.1:
            print('%s - %d VOLUME DISCREPANCY!!! Initial stock [%d] Child Sum Volume [%d] Theo remaining [%f] remaining [%f]. %s %s %s %s %s' % (stock.carbure_client.name, stock.id, stock_initial_volume, child_sum_volume, theo_remaining, remaining, lot.carbure_supplier, lot.carbure_client, lot.period, lot.feedstock.name, lot.biofuel.name))
            assert(False)

    # if is_forwarded, check Child TX (Processing / Trading without storage) and create them
    if tx.is_forwarded:
        try:
            child = LotTransaction.objects.get(parent_tx=tx)
            parent_id = lot.id
            lot.pk = None
            lot.carbure_supplier = lot.carbure_client
            lot.carbure_client = child.carbure_client
            lot.unknown_client = child.unknown_client
            lot.delivery_type = CarbureLot.BLENDING
            lot.parent_lot_id = parent_id
            #print('FORWARD ADD %s %s %f to %s' % (lot.feedstock.name, lot.biofuel.name, lot.volume, lot.delivery_type))            
            lot.save()
            #creation_event = CarbureLotEvent()
            #creation_event.event_type = CarbureLotEvent.CREATED
            #creation_event.event_dt = child.lot.added_time
            #creation_event.user = child.lot.added_by_user
            #creation_event.lot_id = lot.id
            TX_ID_MIGRATED[child.id] = lot.id
        except:
            print('Forwarded TX has not child tx. strange')

    return lot

BULK_COMMENTS = []
BULK_EVENTS = []

def migrate_tx(tx):
    # create the new transaction
    new_tx = create_new_tx_and_child(tx)
    if new_tx is None:
        # new tx is a Stock entry
        return
    # comments migration
    comments = TransactionComment.objects.filter(tx=tx)
    for c in comments:
        new = CarbureLotComment()
        new.entity = c.entity
        new.user = None
        new.lot = new_tx
        new.comment_type = CarbureLotComment.REGULAR
        new.comment_dt = None
        new.comment = c.comment
        new.is_visible_by_admin = True
        new.is_visible_by_auditor = True
        #new.save()
        BULK_COMMENTS.append(new)
    comments = AdminTransactionComment.objects.filter(tx=tx)
    for c in comments:
        new = CarbureLotComment()
        new.entity = c.entity
        new.user = None
        new.lot = new_tx
        if c.entity is not None and c.entity.entity_type == Entity.AUDITOR:
            new.comment_type = CarbureLotComment.AUDITOR
        else:
            new.comment_type = CarbureLotComment.ADMIN
        new.comment_dt = c.datetime
        new.comment = c.comment
        new.is_visible_by_admin = c.is_visible_by_admin
        new.is_visible_by_auditor = c.is_visible_by_auditor
        #new.save()
        BULK_COMMENTS.append(new)
    # events/history migration
    events = TransactionUpdateHistory.objects.filter(tx=tx)
    for e in events:
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.UPDATED
        event.event_dt = e.datetime
        event.lot = new_tx
        event.user = e.modified_by
        event.metadata = {'field': e.field, 'value_before': e.value_before, 'value_after': e.value_after}
        #event.save()
        BULK_EVENTS.append(event)
    # errors
    errors = GenericError.objects.filter(tx=tx).update(lot=new_tx)
    del tx
    del new_tx
    

def migrate_old_data(quick=False):
    global BULK_COMMENTS
    global BULK_EVENTS
    CarbureLot.objects.all().delete()
    if quick:
        all_transactions = LotTransaction.objects.filter(lot__period__startswith='2021', lot__biocarburant__code='ETH')
    else:
        all_transactions = LotTransaction.objects.all()
        paginator = Paginator(LotTransaction.objects.filter(lot__status='Validated'), 1000)
    for page in range(1, paginator.num_pages + 1):
        print('Loading page %d/%d' % (page, paginator.num_pages))
        for tx in tqdm(paginator.page(page).object_list):
            migrate_tx(tx)
            if len(BULK_COMMENTS) > 1000:
                CarbureLotComment.objects.bulk_create(BULK_COMMENTS)
                BULK_COMMENTS = []
            if len(BULK_EVENTS) > 1000:
                CarbureLotEvent.objects.bulk_create(BULK_EVENTS)
                BULK_EVENTS = []
    CarbureLotComment.objects.bulk_create(BULK_COMMENTS)
    CarbureLotEvent.objects.bulk_create(BULK_EVENTS)

if __name__ == '__main__':
    migrate_old_data()
