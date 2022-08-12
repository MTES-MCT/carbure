import sys
import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *

def recalc_all_stocks():
    stocks = CarbureStock.objects.all()
    for stock in stocks:
        child_volume = CarbureLot.objects.filter(parent_stock=stock).exclude(lot_status=CarbureLot.DELETED).aggregate(child_volume=Sum('volume'))
        vol = child_volume['child_volume']
        if vol is None:
            vol = 0
        transformations_volume = CarbureStockTransformation.objects.filter(source_stock=stock).aggregate(vol=Sum('volume_deducted_from_source'))
        if transformations_volume['vol'] is not None:
            vol += transformations_volume['vol']
        initial_volume = stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination
        theo_remaining = initial_volume - vol
        diff = stock.remaining_volume - theo_remaining
        if abs(diff) > 0.1:
            stock.remaining_volume = round(theo_remaining, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()
    
def freeze_old_declarations():
    declarations = SustainabilityDeclaration.objects.filter(period__lt='2022-01-01', declared=False)
    for declaration in declarations:
        period_int = int(declaration.period.year * 100 + declaration.period.month)
        # ensure everything is in order
        pending_reception = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, lot_status=CarbureLot.PENDING).count()
        if pending_reception > 0:
            continue # skip
        pending_correction = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, lot_status__in=[CarbureLot.ACCEPTED], correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]).count()
        if pending_correction > 0:
            continue # skip
        lots_sent_rejected_or_drafts = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, lot_status=CarbureLot.REJECTED).count()
        if lots_sent_rejected_or_drafts > 0:
            continue # skip
        lots_sent_to_fix = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, lot_status__in=[CarbureLot.ACCEPTED], correction_status__in=[CarbureLot.IN_CORRECTION]).count()
        if lots_sent_to_fix > 0:
            continue # skip
        lots_received = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int)
        lots_received.update(declared_by_client=True)
        lots_sent = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int)
        lots_sent.update(declared_by_supplier=True)
        bulk_events = []
        # freeze lots
        lots_to_freeze = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True)
        lots_to_freeze.update(lot_status=CarbureLot.FROZEN)
        lots_to_freeze = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True)
        lots_to_freeze.update(lot_status=CarbureLot.FROZEN)
        # mark declaration
        declaration.declared = True
        declaration.save()
        

if __name__ == '__main__':
    recalc_all_stocks()
    freeze_old_declarations()
    
