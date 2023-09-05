from calendar import calendar
from pydoc import cli
from unittest.util import three_way_cmp
from core.models import CarbureLot, CarbureNotification, SustainabilityDeclaration
import datetime
from django.db.models import Count
from django.db.models import F, Q, When

from elec.models.elec_transfer_certificate import ElecTransferCertificate

def notify_correction_request(lots):
    lots_by_supplier = lots.select_related('carbure_client').filter(carbure_supplier__isnull=False)\
        .values('year', 'carbure_client__name', 'carbure_supplier')\
        .annotate(count=Count('id'), count_frozen=Count('id', filter=Q(lot_status=CarbureLot.FROZEN)))
    for supplier in lots_by_supplier:
        try:
            notif = CarbureNotification.objects.get(dest_id=supplier['carbure_supplier'], type=CarbureNotification.CORRECTION_REQUEST, acked=False, email_sent=False, meta__contains={'client': supplier['carbure_client__name']})
            notif.meta['count'] = notif.meta['count'] + supplier['count']
        except:
            notif = CarbureNotification()
            notif.type = CarbureNotification.CORRECTION_REQUEST
            notif.dest_id = supplier['carbure_supplier']
            notif.send_by_email = True
            notif.notify_administrator = supplier['count_frozen'] > 0
            notif.meta = {'client': supplier['carbure_client__name'], 'count': supplier['count'], 'year': supplier['year']}
        notif.save()

def notify_correction_done(lots):
    lots_by_client = lots.select_related('carbure_supplier').filter(carbure_client__isnull=False)\
        .values('year', 'carbure_client', 'carbure_supplier__name')\
        .annotate(count=Count('id'), count_frozen=Count('id', filter=Q(lot_status=CarbureLot.FROZEN)))
    for client in lots_by_client:
        try:
            notif = CarbureNotification.objects.get(dest_id=client['carbure_client'], type=CarbureNotification.CORRECTION_DONE, acked=False, email_sent=False, meta__contains={'supplier': client['carbure_supplier__name']})
            notif.meta['count'] = notif.meta['count'] + client['count']
        except:
            notif = CarbureNotification()
            notif.type = CarbureNotification.CORRECTION_DONE
            notif.dest_id = client['carbure_client']
            notif.send_by_email = True
            notif.notify_administrator = client['count_frozen'] > 0
            notif.meta = {'supplier': client['carbure_supplier__name'], 'count': client['count'], 'year': client['year']}
        notif.save()

def notify_lots_rejected(lots):
    lots_by_supplier = lots.select_related('carbure_client').filter(carbure_supplier__isnull=False)\
        .values('year', 'carbure_client__name', 'carbure_supplier')\
        .annotate(count=Count('id'), count_frozen=Count('id', filter=Q(lot_status=CarbureLot.FROZEN)))
    for supplier in lots_by_supplier:
        try:
            notif = CarbureNotification.objects.get(dest_id=supplier['carbure_supplier'], type=CarbureNotification.LOTS_REJECTED, acked=False, email_sent=False, meta__contains={'client': supplier['carbure_client__name']})
            notif.meta['count'] = notif.meta['count'] + supplier['count']
        except:
            notif = CarbureNotification()
            notif.type = CarbureNotification.LOTS_REJECTED
            notif.dest_id = supplier['carbure_supplier']
            notif.send_by_email = True
            notif.notify_administrator = supplier['count_frozen'] > 0
            notif.meta = {'client': supplier['carbure_client__name'], 'count': supplier['count'], 'year': supplier['year']}
        notif.save()

def notify_lots_received(lots):
    lots_by_client = lots.filter(carbure_client__isnull=False).select_related('carbure_supplier')\
        .values('year', 'carbure_client', 'carbure_supplier__name')\
        .annotate(count=Count('id'))
    for client in lots_by_client:
        if client['carbure_client'] is None:
            continue
        if client['carbure_supplier__name'] is None: ### batches added to stock
            continue
        try:
            # if the same notif exists
            notif = CarbureNotification.objects.get(dest_id=client['carbure_client'], type=CarbureNotification.LOTS_RECEIVED, acked=False, email_sent=False, meta__contains={'supplier': client['carbure_supplier__name']})
            notif.meta['count'] = notif.meta['count'] + client['count']
        except:
            notif = CarbureNotification()
            notif.type = CarbureNotification.LOTS_RECEIVED
            notif.dest_id = client['carbure_client']
            notif.send_by_email = True
            notif.meta = {'supplier': client['carbure_supplier__name'], 'count': client['count'], 'year': client['year']}
        notif.save()

def notify_lots_recalled(lots):
    lots_by_client = lots.select_related('carbure_supplier').filter(carbure_client__isnull=False)\
        .values('year', 'carbure_client', 'carbure_supplier__name')\
        .annotate(count=Count('id'))
    for client in lots_by_client:
        try:
            notif = CarbureNotification.objects.get(dest_id=client['carbure_client'], type=CarbureNotification.LOTS_RECALLED, acked=False, email_sent=False, meta__contains={'supplier': client['carbure_supplier__name']})
            notif.meta['count'] = notif.meta['count'] + client['count']
        except:
            notif = CarbureNotification()
            notif.type = CarbureNotification.LOTS_RECALLED
            notif.dest_id = client['carbure_client']
            notif.send_by_email = True
            notif.meta = {'supplier': client['carbure_supplier__name'], 'count': client['count'], 'year': client['year']}
        notif.save()

def notify_declaration_cancelled(declaration):
    notif = CarbureNotification()
    notif.type = CarbureNotification.DECLARATION_CANCELLED
    notif.dest = declaration.entity
    notif.send_by_email = False
    notif.notify_administrator = False
    period = declaration.period.year * 100 + declaration.period.month
    notif.meta = {'period': period}
    notif.save()

def notify_declaration_validated(declaration):
    notif = CarbureNotification()
    notif.type = CarbureNotification.DECLARATION_VALIDATED
    notif.dest = declaration.entity
    notif.send_by_email = False
    notif.notify_administrator = False
    period = declaration.period.year * 100 + declaration.period.month
    notif.meta = {'period': period}
    notif.save()

def notify_elec_transfer_certificate(transfer_certificate: ElecTransferCertificate):
    notif = CarbureNotification()
    notif.type = CarbureNotification.DECLARATION_VALIDATED
    notif.dest = transfer_certificate.client
    notif.send_by_email = True
    notif.notify_administrator = False
    notif.meta = {'supplier': transfer_certificate.supplier.name, 'transfer_certificate_id': transfer_certificate.id}
    notif.save()
