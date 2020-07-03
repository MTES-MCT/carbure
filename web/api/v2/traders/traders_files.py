import openpyxl
import datetime
import random
import io

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min

from core.decorators import enrich_with_user_details, restrict_to_traders
from core.xlsx_template import create_template_xlsx_v2_traders, create_template_xlsx_v2_mb

from core.models import Entity, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot
from core.models import LotV2, LotTransaction, TransactionError, LotV2Error


def get_random(model):
    max_id = model.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        element = model.objects.filter(pk=pk).first()
        if element:
            return element


# not an API call. helper function
def load_excel_lot(context, lot_row):
    entity = context['user_entity']
    lot = LotV2()
    lot.added_by = entity
    lot.added_by_user = context['user']
    if 'producer' in lot_row and lot_row['producer'] is not None:
        # this should be a bought or imported lot
        # check if we know the producer
        # producer_is_in_carbure = models.BooleanField(default=True)
        # carbure_producer = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='producer_lotv2')
        # unknown_producer = models.CharField(max_length=64, blank=True, default='')
        if lot_row['producer'] == entity.name:
            # redundant information. by default we assume the producer is the entity logged in
            lot.producer_is_in_carbure = True
            lot.carbure_producer = entity
            lot.unknown_producer = ''
        else:
            # do we know this producer ?
            matches = Entity.objects.filter(name=lot_row['producer']).count()
            if matches == 1:
                # yes we do
                # in this case, the producer should declare its production directly in Carbure
                # we cannot allow someone else to declare for them
                raise Exception("Vous ne pouvez pas déclarer des lots d'un producteur déjà inscrit sur Carbure")
            else:
                # ok, unknown producer. allow importation
                lot.producer_is_in_carbure = False
                lot.carbure_producer = None
                lot.unknown_producer = lot_row['producer']
    elif 'producer' in lot_row and lot_row['producer'] is None:
        lot.producer_is_in_carbure = False
        lot.carbure_producer = None
        lot.unknown_producer = ''
    else:
        # not producer column = simple template
        # current entity is the producer
        lot.producer_is_in_carbure = True
        lot.carbure_producer = entity
        lot.unknown_producer = ''
    lot.save()

    if 'production_site' in lot_row:
        production_site = lot_row['production_site']
        # production_site_is_in_carbure = models.BooleanField(default=True)
        # carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
        # unknown_production_site = models.CharField(max_length=64, blank=True, default='')
        if lot.producer_is_in_carbure:
            try:
                lot.carbure_production_site = ProductionSite.objects.get(producer=lot.carbure_producer, name=production_site)
                lot.production_site_is_in_carbure = True
                lot.unknown_production_site = ''
                LotV2Error.objects.filter(lot=lot, field='production_site').delete()
            except Exception:
                # do not allow the use of an unknown production site if the producer is registered in Carbure
                lot.carbure_production_site = None
                lot.production_site_is_in_carbure = False
                lot.unknown_production_site = ''
                error, c = LotV2Error.objects.update_or_create(lot=lot, field='production_site',
                                                               error='Site de production %s inconnu pour %s' % (production_site, lot.carbure_producer.name),
                                                               defaults={'value': production_site})
        else:
            # producer not in carbure
            # accept any value
            lot.production_site_is_in_carbure = False
            lot.carbure_production_site = None
            if production_site is not None:
                lot.unknown_production_site = production_site
            else:
                lot.unknown_production_site = ''
    else:
        lot.production_site_is_in_carbure = False
        lot.carbure_production_site = None
        lot.unknown_production_site = ''
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='production_site',
                                                       error='Champ production_site introuvable dans le fichier excel',
                                                       defaults={'value': None})
    if lot.producer_is_in_carbure is False:
        if 'production_site_country' in lot_row:
            production_site_country = lot_row['production_site_country']
            if production_site_country is None:
                lot.unknown_production_country = None
            else:
                try:
                    country = Pays.objects.get(code_pays=production_site_country)
                except Exception:
                    error, c = LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_country',
                                                                   error='Champ production_site_country incorrect',
                                                                   defaults={'value': production_site_country})
        else:
            lot.unknown_production_country = None
        if 'production_site_reference' in lot_row:
            lot.unknown_production_site_reference = lot_row['production_site_reference']
        else:
            lot.unknown_production_site_reference = ''
        if 'production_site_commissioning_date' in lot_row:
            lot.unknown_production_site_com_date = lot_row['production_site_commissioning_date']
        else:
            lot.unknown_production_site_com_date = ''
        if 'double_counting_registration' in lot_row:
            lot.unknown_production_site_dbl_counting = lot_row['double_counting_registration']
        else:
            lot.unknown_production_site_dbl_counting = ''

    if 'biocarburant_code' in lot_row:
        biocarburant = lot_row['biocarburant_code']
        try:
            lot.biocarburant = Biocarburant.objects.get(code=biocarburant)
            LotV2Error.objects.filter(lot=lot, field='biocarburant_code').delete()
        except Exception:
            lot.biocarburant = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='biocarburant_code',
                                                           error='Biocarburant inconnu',
                                                           defaults={'value': biocarburant})
    else:
        biocarburant = None
        lot.biocarburant = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='biocarburant_code',
                                                       error='Merci de préciser le Biocarburant',
                                                       defaults={'value': biocarburant})
    if 'matiere_premiere_code' in lot_row:
        matiere_premiere = lot_row['matiere_premiere_code']
        try:
            lot.matiere_premiere = MatierePremiere.objects.get(code=matiere_premiere)
            LotV2Error.objects.filter(lot=lot, field='matiere_premiere_code').delete()
        except Exception:
            lot.matiere_premiere = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere_code',
                                                           error='Matière Première inconnue',
                                                           defaults={'value': matiere_premiere})
    else:
        matiere_premiere = None
        lot.matiere_premiere = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere_code',
                                                       error='Merci de préciser la matière première',
                                                       defaults={'value': matiere_premiere})

    if 'volume' in lot_row:
        volume = lot_row['volume']
        try:
            lot.volume = float(volume)
            LotV2Error.objects.filter(lot=lot, field='volume').delete()
        except Exception:
            lot.volume = 0
            e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                       error='Format du volume incorrect', defaults={'value': volume})
    else:
        e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                   error='Merci de préciser un volume', defaults={'value': volume})

    if 'pays_origine_code' in lot_row:
        pays_origine = lot_row['pays_origine_code']
        try:
            lot.pays_origine = Pays.objects.get(code_pays=pays_origine)
            LotV2Error.objects.filter(lot=lot, field='pays_origine_code').delete()
        except Exception:
            lot.pays_origine = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='pays_origine_code',
                                                           error='Pays inconnu',
                                                           defaults={'value': pays_origine})
    else:
        pays_origine = None
        lot.pays_origine = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='pays_origine_code',
                                                       error='Merci de préciser le pays',
                                                       defaults={'value': pays_origine})
    lot.eec = 0
    if 'eec' in lot_row:
        eec = lot_row['eec']
        try:
            lot.eec = float(eec)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eec',
                                                           error='Format non reconnu',
                                                           defaults={'value': eec})
    lot.el = 0
    if 'el' in lot_row:
        el = lot_row['el']
        try:
            lot.el = float(el)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='el',
                                                           error='Format non reconnu',
                                                           defaults={'value': el})
    lot.ep = 0
    if 'ep' in lot_row:
        ep = lot_row['ep']
        try:
            lot.ep = float(ep)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='ep',
                                                           error='Format non reconnu',
                                                           defaults={'value': ep})
    lot.etd = 0
    if 'etd' in lot_row:
        etd = lot_row['etd']
        try:
            lot.etd = float(etd)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='etd',
                                                           error='Format non reconnu',
                                                           defaults={'value': etd})
    lot.eu = 0
    if 'eu' in lot_row:
        eu = lot_row['eu']
        try:
            lot.eu = float(eu)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eu',
                                                           error='Format non reconnu',
                                                           defaults={'value': eu})
    lot.esca = 0
    if 'esca' in lot_row:
        esca = lot_row['esca']
        try:
            lot.esca = float(esca)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='esca',
                                                           error='Format non reconnu',
                                                           defaults={'value': esca})
    lot.eccs = 0
    if 'eccs' in lot_row:
        eccs = lot_row['eccs']
        try:
            lot.eccs = float(eccs)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eccs',
                                                           error='Format non reconnu',
                                                           defaults={'value': eccs})
    lot.eccr = 0
    if 'eccr' in lot_row:
        eccr = lot_row['eccr']
        try:
            lot.eccr = float(eccr)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eccr',
                                                           error='Format non reconnu',
                                                           defaults={'value': eccr})
    lot.eee = 0
    if 'eee' in lot_row:
        eee = lot_row['eee']
        try:
            lot.eee = float(eee)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eee',
                                                           error='Format non reconnu',
                                                           defaults={'value': eee})
    # calculs ghg
    lot.ghg_total = round(lot.eec + lot.el + lot.ep + lot.etd + lot.eu - lot.esca - lot.eccs - lot.eccr - lot.eee, 2)
    lot.ghg_reference = 83.8
    lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)

    lot.source = 'EXCEL'
    lot.save()

    transaction = LotTransaction()
    transaction.lot = lot
    transaction.save()
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity

    if 'dae' in lot_row:
        dae = lot_row['dae']
        if dae is not None:
            transaction.dae = dae
            TransactionError.objects.filter(tx=transaction, field='dae').delete()
        else:
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                             defaults={'value': dae})
    else:
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                         defaults={'value': None})

    if 'delivery_date' not in lot_row or lot_row['delivery_date'] == '':
        transaction.ea_delivery_date = None
        lot.period = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='ea_delivery_date',
                                                         error="Merci de préciser la date de livraison",
                                                         defaults={'value': None})
    else:
        try:
            delivery_date = lot_row['delivery_date']
            year = int(delivery_date[0:4])
            month = int(delivery_date[5:7])
            day = int(delivery_date[8:10])
            dd = datetime.date(year=year, month=month, day=day)
            transaction.delivery_date = dd
            lot.period = dd.strftime('%Y-%m')
            TransactionError.objects.filter(tx=transaction, field='delivery_date').delete()
        except Exception:
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                             error=msg,
                                                             defaults={'value': delivery_date})
    if 'client' in lot_row and lot_row['client'] is not None:
        client = lot_row['client']
        matches = Entity.objects.filter(name=client).count()
        if matches:
            transaction.client_is_in_carbure = True
            transaction.carbure_client = Entity.objects.get(name=client)
            transaction.unknown_client = ''
        else:
            transaction.client_is_in_carbure = False
            transaction.carbure_client = None
            transaction.unknown_client = client
        TransactionError.objects.filter(tx=transaction, field='client').delete()
    else:
        transaction.client_is_in_carbure = True
        transaction.carbure_client = entity
        transaction.unknown_client = ''

    if 'delivery_site' in lot_row and lot_row['delivery_site'] is not None:
        delivery_site = lot_row['delivery_site']
        matches = Depot.objects.filter(depot_id=delivery_site).count()
        if matches:
            transaction.delivery_site_is_in_carbure = True
            transaction.carbure_delivery_site = Depot.objects.get(depot_id=delivery_site)
            transaction.unknown_client = ''
        else:
            transaction.delivery_site_is_in_carbure = False
            transaction.carbure_delivery_site = None
            transaction.unknown_delivery_site = delivery_site
        TransactionError.objects.filter(tx=transaction, field='delivery_site').delete()
    else:
        transaction.delivery_site_is_in_carbure = False
        transaction.carbure_delivery_site = None
        transaction.unknown_delivery_site = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site',
                                                         defaults={'value': None, 'error': "Merci de préciser un site de livraison"})

    if transaction.delivery_site_is_in_carbure is False:
        if 'delivery_site_country' in lot_row:
            try:
                country = Pays.objects.get(code_pays=lot_row['delivery_site_country'])
                transaction.unknown_delivery_site_country = country
            except Exception:
                error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                     error='Champ production_site_country incorrect',
                                                                     defaults={'value': lot_row['delivery_site_country']})
        else:
            error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                 error='Merci de préciser une valeur dans le champ production_site_country',
                                                                 defaults={'value': None})

    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction

    if 'champ_libre' in lot_row:
        transaction.champ_libre = lot_row['champ_libre']
    transaction.save()
    lot.save()


# not an API call. helper function
def load_excel_mb_lot(context, lot_row):
    entity = context['user_entity']
    # fields
    if 'carbure_id' not in lot_row:
        return False
    carbure_id = lot_row['carbure_id']
    try:
        source_tx = LotTransaction.objects.get(lot__carbure_id=carbure_id)
    except Exception as e:
        print('Could not get lot with carbure_id %s' % (carbure_id))
        print(e)
        return False
    source_lot = LotV2.objects.get(id=source_tx.lot.id)
    lot = source_tx.lot
    if source_tx.carbure_client == context['user_entity'] and source_tx.delivery_status == 'A' and lot.fused_with is None:
        # good
        pass
    else:
        return False

    # okay, source lot exists and is in this user's mass balance
    # duplicate lot
    lot.pk = None
    lot.parent_lot = source_lot
    lot.added_by = entity
    lot.added_by_user = context['user']
    lot.status = 'Draft'
    lot.carbure_id = ''
    lot.is_fused = False
    lot.source = 'EXCEL'
    lot.save()

    if 'volume' in lot_row:
        volume = lot_row['volume']
        try:
            lot.volume = float(volume)
            LotV2Error.objects.filter(lot=lot, field='volume').delete()
        except Exception:
            lot.volume = 0
            e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                       error='Format du volume incorrect', defaults={'value': volume})
    else:
        e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                   error='Merci de préciser un volume', defaults={'value': volume})
    lot.save()

    transaction = LotTransaction()
    transaction.lot = lot
    transaction.save()
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity
    if 'dae' in lot_row:
        dae = lot_row['dae']
        if dae is not None:
            transaction.dae = dae
            TransactionError.objects.filter(tx=transaction, field='dae').delete()
        else:
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                             defaults={'value': dae})
    else:
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                         defaults={'value': None})
    if 'client' in lot_row and lot_row['client'] is not None:
        client = lot_row['client']
        matches = Entity.objects.filter(name=client).count()
        if matches:
            transaction.client_is_in_carbure = True
            transaction.carbure_client = Entity.objects.get(name=client)
            transaction.unknown_client = ''
        else:
            transaction.client_is_in_carbure = False
            transaction.carbure_client = None
            transaction.unknown_client = client
        TransactionError.objects.filter(tx=transaction, field='client').delete()
    else:
        transaction.client_is_in_carbure = False
        transaction.carbure_client = None
        transaction.unknown_client = ''

    if 'delivery_date' not in lot_row or lot_row['delivery_date'] == '':
        transaction.delivery_date = None
        lot.period = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                         error="Merci de préciser la date de livraison",
                                                         defaults={'value': None})
    else:
        try:
            delivery_date = lot_row['delivery_date']
            year = int(delivery_date[0:4])
            month = int(delivery_date[5:7])
            day = int(delivery_date[8:10])
            dd = datetime.date(year=year, month=month, day=day)
            transaction.delivery_date = dd
            lot.period = dd.strftime('%Y-%m')
            TransactionError.objects.filter(tx=transaction, field='delivery_date').delete()
        except Exception:
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                             error=msg,
                                                             defaults={'value': delivery_date})

    if 'delivery_site' in lot_row and lot_row['delivery_site'] is not None:
        delivery_site = lot_row['delivery_site']
        matches = Depot.objects.filter(depot_id=delivery_site).count()
        if matches:
            transaction.delivery_site_is_in_carbure = True
            transaction.carbure_delivery_site = Depot.objects.get(depot_id=delivery_site)
            transaction.unknown_client = ''
        else:
            transaction.delivery_site_is_in_carbure = False
            transaction.carbure_delivery_site = None
            transaction.unknown_delivery_site = delivery_site
        TransactionError.objects.filter(tx=transaction, field='delivery_site').delete()
    else:
        transaction.delivery_site_is_in_carbure = False
        transaction.carbure_delivery_site = None
        transaction.unknown_delivery_site = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site',
                                                         defaults={'value': None, 'error': "Merci de préciser un site de livraison"})

    if transaction.delivery_site_is_in_carbure is False:
        if 'delivery_site_country' in lot_row:
            try:
                country = Pays.objects.get(code_pays=lot_row['delivery_site_country'])
                transaction.unknown_delivery_site_country = country
            except Exception:
                error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                     error='Champ production_site_country incorrect',
                                                                     defaults={'value': lot_row['delivery_site_country']})
        else:
            error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                 error='Merci de préciser une valeur dans le champ production_site_country',
                                                                 defaults={'value': None})

    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction

    if 'champ_libre' in lot_row:
        transaction.champ_libre = lot_row['champ_libre']
    transaction.save()
    lot.save()


@login_required
@enrich_with_user_details
@restrict_to_traders
def excel_template_download(request, *args, **kwargs):
    context = kwargs['context']
    file_location = create_template_xlsx_v2_traders(context['user_entity'])
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_traders.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


@login_required
@enrich_with_user_details
@restrict_to_traders
def excel_template_download_mb(request, *args, **kwargs):
    context = kwargs['context']
    file_location = create_template_xlsx_v2_mb(context['user_entity'])
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_mb.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


@login_required
@enrich_with_user_details
@restrict_to_traders
def excel_template_upload(request, *args, **kwargs):
    context = kwargs['context']
    file = request.FILES.get('file')
    if file is None:
        return JsonResponse({'status': "error", 'message': "Merci d'ajouter un fichier"}, status=400)
    # we can load the file
    wb = openpyxl.load_workbook(file)
    lots_sheet = wb['lots']
    colid2field = {}
    lots = []
    # create a dictionary from the line
    for i, row in enumerate(lots_sheet):
        if i == 0:
            # header
            for i, col in enumerate(row):
                colid2field[i] = col.value
        else:
            lot = {}
            for i, col in enumerate(row):
                field = colid2field[i]
                lot[field] = col.value
            lots.append(lot)
    total_lots = len(lots)
    lots_loaded = 0
    for lot in lots:
        try:
            load_excel_lot(context, lot)
            lots_loaded += 1
        except Exception as e:
            print(e)
    return JsonResponse({'status': "success", 'message': "%d/%d lots chargés correctement" % (lots_loaded, total_lots)})


@login_required
@enrich_with_user_details
@restrict_to_traders
def excel_mb_template_upload(request, *args, **kwargs):
    context = kwargs['context']
    file = request.FILES.get('file')
    if file is None:
        return JsonResponse({'status': "error", 'message': "Merci d'ajouter un fichier"}, status=400)
    # we can load the file
    wb = openpyxl.load_workbook(file)
    lots_sheet = wb['lots']
    colid2field = {}
    lots = []
    # create a dictionary from the line
    for i, row in enumerate(lots_sheet):
        if i == 0:
            # header
            for i, col in enumerate(row):
                colid2field[i] = col.value
        else:
            lot = {}
            for i, col in enumerate(row):
                field = colid2field[i]
                lot[field] = col.value
            lots.append(lot)
    total_lots = len(lots)
    lots_loaded = 0
    for lot in lots:
        try:
            load_excel_mb_lot(context, lot)
            lots_loaded += 1
        except Exception as e:
            print(e)
    return JsonResponse({'status': "success", 'message': "%d/%d lots chargés correctement" % (lots_loaded, total_lots)})


@login_required
@enrich_with_user_details
@restrict_to_traders
def export_in(request, *args, **kwargs):
    context = kwargs['context']
    today = datetime.datetime.now()
    filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))

    transactions = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated")

    buffer = io.BytesIO()
    header = "producer;production_site;production_site_country;production_site_reference;production_site_commissioning_date;double_counting_registration;volume;biocarburant_code;\
              matiere_premiere_code;pays_origine_code;eec;el;ep;etd;eu;esca;eccs;eccr;eee;e;dae;champ_libre;client;delivery_date;delivery_site;delivery_site_country\n"
    buffer.write(header.encode())
    for tx in transactions:
        lot = tx.lot
        line = [lot.carbure_producer.name if lot.producer_is_in_carbure else lot.unknown_producer,
                lot.carbure_production_site.name if lot.production_site_is_in_carbure else lot.unknown_production_site,
                lot.carbure_production_site.country.code_pays if lot.production_site_is_in_carbure and lot.carbure_production_site.country else lot.unknown_production_country.code_pays if lot.unknown_production_country else '',
                lot.unknown_production_site_reference,
                lot.unknown_production_site_com_date,
                lot.unknown_production_site_dbl_counting,
                lot.volume,
                lot.biocarburant.code if lot.biocarburant else '',
                lot.matiere_premiere.code if lot.matiere_premiere else '',
                lot.pays_origine.code_pays if lot.pays_origine else '',
                lot.eec, lot.el, lot.ep, lot.etd, lot.eu, lot.esca,
                lot.eccs, lot.eccr, lot.eee, lot.ghg_total,
                # tx
                tx.dae,
                tx.champ_libre,
                tx.carbure_client.name if tx.client_is_in_carbure else tx.unknown_client,
                tx.delivery_date,
                tx.carbure_delivery_site.depot_id if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site,
                tx.carbure_delivery_site.country.code_pays if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site_country
                ]
        csvline = '%s\n' % (';'.join([str(k) for k in line]))
        buffer.write(csvline.encode('iso-8859-1'))
    csvfile = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    response.write(csvfile)
    return response


@login_required
@enrich_with_user_details
@restrict_to_traders
def export_drafts(request, *args, **kwargs):
    context = kwargs['context']
    today = datetime.datetime.now()
    filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))

    lots = LotV2.objects.filter(added_by=context['user_entity'], status='Draft')
    transactions_ids = set([tx['id__min'] for tx in LotTransaction.objects.filter(lot__in=lots).values('lot_id', 'id').annotate(Min('id'))])
    transactions = {tx.lot: tx for tx in LotTransaction.objects.filter(id__in=transactions_ids)}

    buffer = io.BytesIO()
    header = "producer;production_site;production_site_country;production_site_reference;production_site_commissioning_date;double_counting_registration;volume;biocarburant_code;\
              matiere_premiere_code;pays_origine_code;eec;el;ep;etd;eu;esca;eccs;eccr;eee;e;dae;champ_libre;client;delivery_date;delivery_site;delivery_site_country\n"
    buffer.write(header.encode())
    for lot in lots:
        if lot not in transactions:
            continue
        tx = transactions[lot]
        line = [lot.carbure_producer.name if lot.producer_is_in_carbure else lot.unknown_producer,
                lot.carbure_production_site.name if lot.production_site_is_in_carbure else lot.unknown_production_site,
                lot.carbure_production_site.country.code_pays if lot.production_site_is_in_carbure and lot.carbure_production_site.country else lot.unknown_production_country.code_pays if lot.unknown_production_country else '',
                lot.unknown_production_site_reference,
                lot.unknown_production_site_com_date,
                lot.unknown_production_site_dbl_counting,
                lot.volume,
                lot.biocarburant.code if lot.biocarburant else '',
                lot.matiere_premiere.code if lot.matiere_premiere else '',
                lot.pays_origine.code_pays if lot.pays_origine else '',
                lot.eec, lot.el, lot.ep, lot.etd, lot.eu, lot.esca,
                lot.eccs, lot.eccr, lot.eee, lot.ghg_total,
                # tx
                tx.dae,
                tx.champ_libre,
                tx.carbure_client.name if tx.client_is_in_carbure else tx.unknown_client,
                tx.delivery_date,
                tx.carbure_delivery_site.depot_id if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site,
                tx.carbure_delivery_site.country.code_pays if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site_country
                ]
        csvline = '%s\n' % (';'.join([str(k) for k in line]))
        buffer.write(csvline.encode('iso-8859-1'))
    csvfile = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    response.write(csvfile)
    return response


@login_required
@enrich_with_user_details
@restrict_to_traders
def export_mb(request, *args, **kwargs):
    context = kwargs['context']
    today = datetime.datetime.now()
    filename = 'export_mb_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))

    transactions = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated")
    buffer = io.BytesIO()
    header = "carbure_id;producer;production_site;production_site_country;production_site_reference;production_site_commissioning_date;double_counting_registration;volume;biocarburant_code;\
              matiere_premiere_code;pays_origine_code;eec;el;ep;etd;eu;esca;eccs;eccr;eee;e;dae;champ_libre;client;delivery_date;delivery_site;delivery_site_country\n"
    buffer.write(header.encode())
    for tx in transactions:
        lot = tx.lot
        line = [lot.carbure_id,
                lot.carbure_producer.name if lot.carbure_producer else lot.unknown_producer,
                lot.carbure_production_site.name if lot.carbure_production_site else lot.unknown_production_site,
                lot.carbure_production_site.country.code_pays if lot.carbure_production_site and lot.carbure_production_site.country else lot.unknown_production_country.code_pays if lot.unknown_production_country else '',
                lot.unknown_production_site_reference,
                lot.unknown_production_site_com_date,
                lot.unknown_production_site_dbl_counting,
                lot.volume,
                lot.biocarburant.code if lot.biocarburant else '',
                lot.matiere_premiere.code if lot.matiere_premiere else '',
                lot.pays_origine.code_pays if lot.pays_origine else '',
                lot.eec, lot.el, lot.ep, lot.etd, lot.eu, lot.esca,
                lot.eccs, lot.eccr, lot.eee, lot.ghg_total,
                # tx
                tx.dae,
                tx.champ_libre,
                tx.carbure_client.name if tx.client_is_in_carbure else tx.unknown_client,
                tx.delivery_date,
                tx.carbure_delivery_site.depot_id if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site,
                tx.carbure_delivery_site.country.code_pays if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site_country.code_pays if tx.unknown_delivery_site_country else ''
                ]
        csvline = '%s\n' % (';'.join([str(k) for k in line]))
        buffer.write(csvline.encode('iso-8859-1'))
    csvfile = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    response.write(csvfile)
    return response


@login_required
@enrich_with_user_details
@restrict_to_traders
def export_out(request, *args, **kwargs):
    context = kwargs['context']
    today = datetime.datetime.now()
    filename = 'export_histo_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))

    transactions = LotTransaction.objects.filter(carbure_vendor=context['user_entity'], lot__status='Validated')
    buffer = io.BytesIO()
    header = "carbure_id;producer;production_site;production_site_country;production_site_reference;production_site_commissioning_date;double_counting_registration;volume;biocarburant_code;\
              matiere_premiere_code;pays_origine_code;eec;el;ep;etd;eu;esca;eccs;eccr;eee;e;dae;champ_libre;client;delivery_date;delivery_site;delivery_site_country\n"
    buffer.write(header.encode())
    for tx in transactions:
        lot = tx.lot
        line = [lot.carbure_id,
                lot.carbure_producer.name if lot.carbure_producer else lot.unknown_producer,
                lot.carbure_production_site.name if lot.carbure_production_site else lot.unknown_production_site,
                lot.carbure_production_site.country.code_pays if lot.carbure_production_site and lot.carbure_production_site.country else lot.unknown_production_country.code_pays if lot.unknown_production_country else '',
                lot.unknown_production_site_reference,
                lot.unknown_production_site_com_date,
                lot.unknown_production_site_dbl_counting,
                lot.volume,
                lot.biocarburant.code if lot.biocarburant else '',
                lot.matiere_premiere.code if lot.matiere_premiere else '',
                lot.pays_origine.code_pays if lot.pays_origine else '',
                lot.eec, lot.el, lot.ep, lot.etd, lot.eu, lot.esca,
                lot.eccs, lot.eccr, lot.eee, lot.ghg_total,
                # tx
                tx.dae,
                tx.champ_libre,
                tx.carbure_client.name if tx.client_is_in_carbure else tx.unknown_client,
                tx.delivery_date,
                tx.carbure_delivery_site.depot_id if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site,
                tx.carbure_delivery_site.country.code_pays if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site_country.code_pays if tx.unknown_delivery_site_country else ''
                ]
        csvline = '%s\n' % (';'.join([str(k) for k in line]))
        buffer.write(csvline.encode('iso-8859-1'))
    csvfile = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    response.write(csvfile)
    return response
