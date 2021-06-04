from core.models import LotTransaction, EmailNotification

def notify_lots_rejected(txs):
    for tx in txs:
        # create email notif to tx creator
        n = EmailNotification()
        n.linked_tx = tx
        n.notif_type = EmailNotification.LOT_REJECTED
        n.entity = tx.carbure_vendor
        n.save()

def notify_accepted_lot_in_correction(tx):
    recipients = [ur.user.email for ur in UserRights.objects.filter(entity=tx.carbure_vendor, user__is_staff=False)]
    cc = []
    if tx.carbure_client:
        cc += [ur.user.email for ur in UserRights.objects.filter(entity=tx.carbure_client, user__is_staff=False)]

    if tx.delivery_status == LotTransaction.FROZEN:
        # add administration in copy
        cc += 'carbure@beta.gouv.fr'

    #send_accepted_lot_in_correction_email(tx, recipients, cc)

def notify_declaration_invalidated(tx, entity):
    year, month = tx.lot.period.split('-')
    period = datetime.date(year=year, month=int(month), day=1)
    try:
        sd = SustainabilityDeclaration.objects.filter(entity=entity, period=period)
        sd.declared = False
        sd.checked = False
        sd.save()
    except:
        # declaration doesn't exist ?
        pass    
    EmailNotification.objects.create()
    EmailNotification.objects.create()    

def notify_declaration_validated(declaration):
    pass