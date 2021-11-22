from core.models import CarbureLot, CarbureStock


def construct_carbure_lot(prefetched_data, entity, data):
    errors = []

    lot = CarbureLot()
    lot.added_by = entity

    if 'parent_stock_id' in data:
        try:
            parent_stock = CarbureStock.objects.get(id=data['parent_stock_id'])
            assert(parent_stock.carbure_client == entity)
        except:
            return False


    # do not allow to modify production data for stock-lots
    if lot.parent_lot == None:
        errors += fill_producer_info(entity, lot_dict, lot, prefetched_data)
        errors += fill_production_site_info(entity, lot_dict, lot, tx, prefetched_data)
        errors += fill_supplier_info(entity, lot_dict, lot, prefetched_data)
        errors += fill_biocarburant_info(lot_dict, lot, tx, prefetched_data)
        errors += fill_matiere_premiere_info(lot_dict, lot, tx, prefetched_data)
        errors += fill_pays_origine_info(lot_dict, lot, tx, prefetched_data)
        errors += fill_ghg_info(lot_dict, lot, tx)
        errors += fill_volume_info(lot_dict, lot, tx)
    else:
        # STOCK// if someone updates the volume of a validated split-lot
        # STOCK// we first recredit the volume back in stock
        if lot.status == LotV2.VALIDATED and lot.is_split:
            lot.parent_lot.remaining_volume += lot.volume
            lot.parent_lot.remaining_volume = round(lot.parent_lot.remaining_volume, 2)
            lot.parent_lot.save()
        # STOCK// only the lot.added_by can update the volume of a split transaction
        if lot.added_by == entity and lot.is_split:
            errors += fill_volume_info(lot_dict, lot, tx)
        # STOCK// and debit the stock back according to new volume
        if lot.status == LotV2.VALIDATED and lot.is_split:
            lot.parent_lot.remaining_volume -= lot.volume
            lot.parent_lot.remaining_volume = round(lot.parent_lot.remaining_volume, 2)
            lot.parent_lot.save()

    # data related to TRANSACTION

    if tx.carbure_vendor and tx.carbure_vendor == entity:
        # I am the seller
        can_update_tx = True
    if not tx.carbure_vendor and tx.carbure_client and tx.carbure_client == entity:
        # lot added by client, he's allowed to update
        can_update_tx = True
    if can_update_tx:
        fill_mac_data(lot_dict, tx) # does not return anything
        errors += fill_dae_data(lot_dict, tx)
        errors += fill_delivery_date(lot_dict, lot, tx)
        errors += fill_client_data(entity, lot_dict, tx, prefetched_data)
        errors += fill_vendor_data(entity, lot_dict, tx, prefetched_data)
        errors += fill_delivery_site_data(lot_dict, tx, prefetched_data)
        tx.ghg_total = lot.ghg_total
        tx.ghg_reduction = lot.ghg_reduction
        tx.champ_libre = lot_dict['champ_libre'] if 'champ_libre' in lot_dict else ''

    return lot, tx, errors

def bulk_insert_lots(entity, lots, errors, prefetched_data):
    pass
