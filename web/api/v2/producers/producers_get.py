from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from core.decorators import enrich_with_user_details, restrict_to_producers, get_producer_corrections

from core.models import Pays, Entity, Depot, LotV2, LotTransaction, LotV2Error, TransactionComment


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_drafts(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(lot__added_by=context['user_entity'], lot__status='Draft')
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    comments_tx_added = TransactionComment.objects.filter(tx__in=transactions, topic__in=['SUSTAINABILITY', 'BOTH'])
    commentssez = serializers.serialize('json', comments_tx_added, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez, 'comments': commentssez})


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
    anon, created = Entity.objects.get_or_create(name='Confidentiel', entity_type='Producteur')
    france = Pays.objects.get(code_pays='FR')
    anon_site, created = Depot.objects.get_or_create(name='Confidentiel', depot_id='0', country=france)

    transactions, comments = get_producer_corrections(context['user_entity'])

    # anonymisation des données
    processed_tx = []
    for t in transactions:
        # est-ce un de mes lots qui a été revendu ?
        if t.carbure_vendor != context['user_entity']:
            # on récupère le DAE initial
            initial_tx = LotTransaction.objects.filter(lot=t.lot).order_by('delivery_date')[0]
            #### OU ---
            # on rend les données confidentielles mais on utilise le DAE initial
            t.carbure_client = anon
            t.dae = initial_tx.dae
            t.client_is_in_carbure = True
            t.delivery_site_is_in_carbure = True
            t.carbure_delivery_site = anon_site
            t.unknown_client = 'Confidentiel'
            t.unknown_delivery_site = 'Confidentiel'
            t.unknown_delivery_site_country = france
            t.champ_libre = ''
            t.delivery_date = None
        processed_tx.append(t)

    processed_comments = []
    for c in comments:
        if c.tx.carbure_vendor != context['user_entity'] and c.entity != context['user_entity']:
            c.entity = anon
        processed_comments.append(c)
    txsez = serializers.serialize('json', processed_tx, use_natural_foreign_keys=True)
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
