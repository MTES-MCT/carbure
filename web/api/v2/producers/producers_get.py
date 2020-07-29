from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from itertools import chain

from core.decorators import enrich_with_user_details, restrict_to_producers

from core.models import LotV2, LotTransaction, LotV2Error, TransactionComment


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_drafts(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(lot__added_by=context['user_entity'], lot__status='Draft')
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_mb_drafts(request, *args, **kwargs):
    context = kwargs['context']
    tx = LotTransaction.objects.filter(lot__added_by=context['user_entity'], lot__status='Draft').exclude(lot__parent_lot=None)
    txsez = serializers.serialize('json', tx, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_in(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated")
    comments = TransactionComment.objects.filter(tx__in=transactions)
    lot_ids = [t.lot.id for t in transactions]
    lots = LotV2.objects.filter(id__in=lot_ids)
    errors = LotV2Error.objects.filter(lot__in=lots)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    errsez = serializers.serialize('json', errors, use_natural_foreign_keys=True)
    commentssez = serializers.serialize('json', comments, use_natural_foreign_keys=True)
    return JsonResponse({'errors': errsez, 'transactions': txsez, 'comments': commentssez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_mb(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated", lot__fused_with=None, lot__volume__gt=0)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_corrections(request, *args, **kwargs):
    context = kwargs['context']
    # corrections de type "Durabilite" ou "Les deux" pour mes lots
    tx_added = LotTransaction.objects.filter(lot__data_origin_entity=context['user_entity'], delivery_status__in=['R', 'AC', 'AA'], lot__status="Validated")
    comments_tx_added = TransactionComment.objects.filter(tx__in=tx_added, topic__in=['SUSTAINABILITY', 'BOTH'])

    # corrections de type "Transaction" ou "les deux" pour les lots vendus
    tx_sold = LotTransaction.objects.filter(carbure_vendor=context['user_entity'], delivery_status__in=['R', 'AC', 'AA'], lot__status="Validated")
    comments_tx_sold = TransactionComment.objects.filter(tx__in=tx_sold, topic__in=['TX', 'BOTH'])

    # union de tout ça
    transactions = set(list(chain(tx_added, tx_sold)))
    comments = set(list(chain(comments_tx_added, comments_tx_sold)))
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    commentssez = serializers.serialize('json', comments, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez, 'comments': commentssez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_out(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(carbure_vendor=context['user_entity'], lot__status='Validated')
    comments = TransactionComment.objects.filter(tx__in=transactions)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    commentssez = serializers.serialize('json', comments, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez, 'comments': commentssez})
