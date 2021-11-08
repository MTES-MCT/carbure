# Generated by Django 3.2.8 on 2021-11-05 14:29

from django.db import migrations
import datetime
import calendar

from django.db.models.aggregates import Sum

from core.models import AdminTransactionComment, CarbureLot, CarbureLotComment, CarbureLotEvent, CarbureStock, CarbureStockTransformation, ETBETransformation, Entity, GenericError, LotTransaction, LotV2, TransactionComment, TransactionUpdateHistory

# map old id to new id
TX_ID_MIGRATED = {}

def create_new_tx_and_child(tx):
    if tx.id in TX_ID_MIGRATED:
        # ignore, this is a child tx already migrated
        print('Ignoring txid %d - already migrated' % (tx.id))
        new_id = TX_ID_MIGRATED[tx.id]
        if new_id:
            return CarbureLot.objects.get(id=TX_ID_MIGRATED[tx.id])
        else:
            return None
    print('Migrate txid %d' % (tx.id))
    lot = CarbureLot()
    lot.period = tx.delivery_date.year * 100 + tx.delivery_date.month
    lot.year = tx.delivery_date.year
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
    lot.delivery_date = tx.delivery_date
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
    if tx.is_mac:
        lot.delivery_type = CarbureLot.RFC
    if tx.is_stock:
        lot.delivery_type = CarbureLot.STOCK
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
        creation_event = CarbureLotEvent()
        creation_event.event_type = CarbureLotEvent.CREATED
        creation_event.event_dt = tx.lot.added_time
        creation_event.user = tx.lot.added_by_user
        creation_event.lot_id = first_tx_id
        lot.pk = None
        lot.parent_lot_id = first_tx_id
    lot.carbure_supplier = tx.carbure_vendor
    lot.supplier_certificate = tx.carbure_vendor_certificate
    lot.supplier_certificate_type = None
    lot.save()
    creation_event = CarbureLotEvent()
    creation_event.event_type = CarbureLotEvent.CREATED
    creation_event.event_dt = tx.lot.added_time
    creation_event.user = tx.lot.added_by_user
    creation_event.lot_id = lot.id
    TX_ID_MIGRATED[tx.id] = lot.id



    # for each TX
    # if is_stock, create stock, get child tx, link them to stock, check remaining volume
    if lot.delivery_type == CarbureLot.STOCK:
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

        if tx.lot.biocarburant.code == 'ETH':
            # check if I have been transformed into ETBE
            if ETBETransformation.objects.filter(previous_stock=tx.id).exists():
                transformations = ETBETransformation.objects.filter(previous_stock=tx.id)
                for trans in transformations:
                    print('This ETH stock was converted to ETBE!')
                    
                    # create new stock
                    child = trans.new_stock
                    etbe_stock = CarbureStock()
                    etbe_stock.parent_lot = None
                    etbe_stock.parent_transformation = None
                    etbe_stock.carbure_id = lot.carbure_id
                    etbe_stock.depot = lot.carbure_delivery_site
                    etbe_stock.carbure_client = lot.carbure_client
                    etbe_stock.remaining_volume = child.lot.remaining_volume
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

        child = LotTransaction.objects.filter(parent_tx=tx)
        child_sum_volume = 0
        for c in child:
            lot.pk = None
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
            lot.save()
            creation_event = CarbureLotEvent()
            creation_event.event_type = CarbureLotEvent.CREATED
            creation_event.event_dt = c.lot.added_time
            creation_event.user = c.lot.added_by_user
            creation_event.lot_id = lot.id            
            TX_ID_MIGRATED[c.id] = lot.id
            child_sum_volume += c.lot.volume

        theo_remaining = stock.parent_lot.volume - child_sum_volume
        remaining = stock.remaining_volume
        diff = remaining - theo_remaining
        if abs(diff) > 0.1:
            print('VOLUME DISCREPANCY!!! Theo remaining [%f] remaining [%f]' % (theo_remaining, remaining))

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
            lot.save()
            creation_event = CarbureLotEvent()
            creation_event.event_type = CarbureLotEvent.CREATED
            creation_event.event_dt = child.lot.added_time
            creation_event.user = child.lot.added_by_user
            creation_event.lot_id = lot.id
            TX_ID_MIGRATED[child.id] = lot.id
        except:
            print('Forwarded TX has not child tx. strange')

    return lot


def migrate_old_data(apps, schema_editor):
    #all_transactions = LotTransaction.objects.all()
    all_transactions = LotTransaction.objects.filter(lot__year=2021, lot__status=LotV2.VALIDATED)
    for tx in all_transactions:
        # create the new transaction
        new_tx = create_new_tx_and_child(tx)
        if new_tx is None:
            # new tx is a Stock entry
            continue
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
            new.save()
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
            new.save()
        # events/history migration
        events = TransactionUpdateHistory.objects.filter(tx=tx)
        for e in events:
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.UPDATED
            event.event_dt = e.datetime
            event.lot = new_tx
            event.user = e.modified_by
            event.metadata = {'field': e.field, 'value_before': e.value_before, 'value_after': e.value_after}
            event.save()
        # errors
        errors = GenericError.objects.filter(tx=tx).update(lot=new_tx)

def ensure_data_consistency(apps, schema_editor):
    # the goal is to ensure that Volume IN equals Volume Stock + Volume Out for every single entity
    entities = Entity.objects.all()
    for entity in entities:
        tx_in = CarbureLot.objects.filter(carbure_client=entity).aggregate(volume_in=Sum('volume'))
        tx_out = CarbureLot.objects.filter(carbure_supplier=entity).aggregate(volume_out=Sum('remaining_volume'))
        stock = CarbureStock.objects.filter(carbure_client=entity).aggregate(volume_stock=Sum('volume'))

        diff = tx_in['volume_in'] - (tx_out['volume_out'] + stock['volume_stock'])
        if abs(diff) > 0.1:
            print('%s - Volumes inconsistent: in [%.2f] out + stock [%.2f]' % (entity.name, tx_in['volume_in'], (tx_out['volume_out'] + stock['volume_stock'])))
            return 1
        else:
            print('Volumes OK for %s' % (entity.name))

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0192_auto_20211106_1137'),
    ]

    operations = [
        migrations.RunPython(migrate_old_data),
        #migrations.RunPython(ensure_data_consistency),
    ]
