from calendar import calendar
from core.models import LotTransaction, EmailNotification, UserRights, SustainabilityDeclaration
import datetime


def notify_lots_rejected(txs):
    for tx in txs:
        # create email notif to tx creator
        n = EmailNotification()
        n.linked_tx = tx
        n.notif_type = EmailNotification.LOT_REJECTED
        n.entity = tx.carbure_vendor
        if n.entity and n.entity.notifications_enabled:
            n.save()


# demande de correction
def notify_lot_in_correction(tx):
    n = EmailNotification()
    n.linked_tx = tx
    n.notif_type = EmailNotification.CORRECTION_REQUEST
    n.entity = tx.carbure_vendor
    if not n.entity:
        n.entity = tx.carbure_client
    if tx.delivery_status == LotTransaction.FROZEN:
        n.send_copy_to_admin = True
    if n.entity and n.entity.notifications_enabled:
        n.save()

def notify_lot_fixed(tx):
    n = EmailNotification()
    n.linked_tx = tx
    n.notif_type = EmailNotification.CORRECTION_DONE
    n.entity = tx.carbure_client
    if n.entity and n.entity.notifications_enabled:
        n.save()    

def notify_declaration_invalidated(tx, entity):
    year, month = tx.lot.period.split('-')
    period = datetime.date(year=int(year), month=int(month), day=1)
    try:
        sd = SustainabilityDeclaration.objects.filter(entity=entity, period=period)
        sd.declared = False
        sd.checked = False
        sd.save()
    except:
        # declaration doesn't exist ?
        nextmonth = period + datetime.timedelta(days=31)
        (weekday, lastday) = calendar.monthrange(nextmonth.year, nextmonth.month)
        deadline = datetime.date(year=nextmonth.year, month=nextmonth.month, day=lastday)   
        sd = SustainabilityDeclaration.objects.create(entity=entity, period=period, deadline=deadline)
    n = EmailNotification()
    n.linked_declaration = sd
    n.notif_type = EmailNotification.DECLARATION_INVALIDATED
    n.entity = entity
    n.send_copy_to_admin = True
    if n.entity and n.entity.notifications_enabled:
        n.save()

def notify_declaration_validated(declaration):
    n = EmailNotification()
    n.notif_type = EmailNotification.DECLARATION_VALIDATED
    n.linked_declaration = declaration
    n.entity = declaration.entity
    n.send_copy_to_admin = True
    if n.entity and n.entity.notifications_enabled:
        n.save()


def notify_pending_lot(tx):
    # create email notif to tx client
    n = EmailNotification()
    n.linked_tx = tx
    n.notif_type = EmailNotification.LOT_PENDING
    n.entity = tx.carbure_client
    if n.entity and n.entity.notifications_enabled:
        n.save()

def notify_lot_fixed(tx):
    # create email notif to tx client
    n = EmailNotification()
    n.linked_tx = tx
    n.notif_type = EmailNotification.CORRECTION_DONE
    n.entity = tx.carbure_client
    if n.entity and n.entity.notifications_enabled:
        n.save()
