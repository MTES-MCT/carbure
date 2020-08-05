import datetime

from core.models import LotV2


def tx_is_valid(tx):
    # make sure all mandatory fields are set
    if not tx.dae:
        return False, 'DAE manquant'
    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
        return False, 'Site de livraison manquant'
    if tx.delivery_site_is_in_carbure and not tx.carbure_delivery_site:
        return False, 'Site de livraison manquant'
    if not tx.delivery_date:
        return False, 'Date de livraison manquante'
    if tx.client_is_in_carbure and not tx.carbure_client:
        return False, 'Veuillez renseigner un client'
    if not tx.client_is_in_carbure and not tx.unknown_client:
        return False, 'Veuillez renseigner un client'

    if tx.unknown_delivery_site_country is not None and tx.unknown_delivery_site_country.is_in_europe and tx.lot.pays_origine is None:
        return False, "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
    if tx.carbure_delivery_site is not None and tx.carbure_delivery_site.country.is_in_europe and tx.lot.pays_origine is None:
        return False, "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
    return True, ''


def lot_is_valid(lot):
    if not lot.volume:
        return False, 'Veuillez renseigner le volume'

    if not lot.parent_lot:
        if not lot.biocarburant:
            return False, 'Veuillez renseigner le type de biocarburant'
        if not lot.matiere_premiere:
            return False, 'Veuillez renseigner la matière première'
        if lot.producer_is_in_carbure and lot.carbure_production_site is None:
            return False, 'Veuillez préciser le site de production'
    else:
        # no need to check lot info
        pass
    return True, ''


def generate_carbure_id(lot):
    today = datetime.date.today()
    # [PAYS][YYMM]P[IDProd]-[1....]-([S123])
    # FR2002P001-1
    country = 'XX'
    if lot.carbure_production_site and lot.carbure_production_site.country:
        country = lot.carbure_production_site.country.code_pays
    yymm = today.strftime('%y%m')
    idprod = 'XXX'
    if lot.carbure_producer:
        idprod = '%d' % (lot.carbure_producer.id)
    return "%s%sP%s-%d" % (country, yymm, idprod, lot.id)


def fuse_lots(txs):
    new_lot = LotV2()
    new_lot.save()

    total_volume = 0
    for tx in txs:
        total_volume += tx.lot.volume
        tx.lot.is_fused = True
        tx.lot.fused_with = new_lot
        tx.lot.save()

    # fill lot details
    lot = txs[0].lot
    new_lot.volume = total_volume
    new_lot.period = lot.period
    new_lot.producer_is_in_carbure = lot.producer_is_in_carbure
    new_lot.carbure_producer = lot.carbure_producer
    new_lot.unknown_producer = lot.unknown_producer
    new_lot.production_site_is_in_carbure = lot.production_site_is_in_carbure
    new_lot.carbure_production_site = lot.carbure_production_site
    new_lot.unknown_production_site = lot.unknown_production_site
    new_lot.unknown_production_site_com_date = lot.unknown_production_site_com_date
    new_lot.unknown_production_site_reference = lot.unknown_production_site_reference
    new_lot.unknown_production_site_dbl_counting = lot.unknown_production_site_dbl_counting
    new_lot.matiere_premiere = lot.matiere_premiere
    new_lot.biocarburant = lot.biocarburant
    new_lot.pays_origine = lot.pays_origine
    new_lot.eec = lot.eec
    new_lot.el = lot.el
    new_lot.ep = lot.ep
    new_lot.etd = lot.etd
    new_lot.eu = lot.eu
    new_lot.esca = lot.esca
    new_lot.eccs = lot.eccs
    new_lot.eccr = lot.eccr
    new_lot.eee = lot.eee
    new_lot.ghg_total = lot.ghg_total
    new_lot.ghg_reduction = lot.ghg_reduction
    new_lot.ghg_reference = lot.ghg_reference
    new_lot.status = 'Validated'
    new_lot.source = 'FUSION'
    new_lot.added_by = lot.added_by
    new_lot.added_by_user = lot.added_by_user
    new_lot.is_fused = False
    new_lot.fused_with = None
    new_lot.save()

    # create a new TX
    new_tx = txs[0]
    new_tx.pk = None
    new_tx.dae = ''
    new_tx.lot = new_lot
    new_tx.save()
    new_lot.carbure_id = generate_carbure_id(new_lot) + 'F'
    new_lot.save()
    print('new lot of %d of %s id %s' % (new_lot.volume, new_lot.biocarburant.name, new_lot.carbure_id))
