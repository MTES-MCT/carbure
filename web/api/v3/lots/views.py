from django.http import JsonResponse
from core.models import LotTransaction, Entity, UserRights, MatierePremiere, Biocarburant, Pays


def get_lots(request):
    return JsonResponse({'status': 'success'})


def get_snapshot(request):
    data = {}

    producer = request.GET.get('producer_id', False)
    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer_id"}, status=400)
    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(lot__carbure_producer=producer)

    drafts = len(txs.filter(lot__status='Draft'))
    validated = len(txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA']))
    tofix = len(txs.filter(lot__status='Validated', delivery_status='AC'))
    accepted = len(txs.filter(lot__status='Validated', delivery_status='A'))
    data['lots'] = {'drafts': drafts, 'validated': validated, 'tofix': tofix, 'accepted': accepted}

    mps = [m.natural_key() for m in MatierePremiere.objects.filter(id__in=txs.values('lot__matiere_premiere').distinct())]
    bcs = [b.natural_key() for b in Biocarburant.objects.filter(id__in=txs.values('lot__biocarburant').distinct())]
    periods = [p for p in txs.values('lot__period').distinct()]
    countries = [c.natural_key() for c in Pays.objects.filter(id__in=txs.values('lot__pays_origine').distinct())]
    c1 = txs.values('carbure_client__name').distinct()
    c2 = txs.values('unknown_client').distinct()
    clients = list(c1)+list(c2)

    ps1 = txs.values('lot__carbure_production_site__name').distinct()
    ps2 = txs.values('lot__unknown_production_site').distinct()
    psites = list(ps1) + list(ps2)
    data['filters'] = {'matieres_premieres': mps, 'biocarburants': bcs, 'periods': periods, 'production_sites': psites, 'countries_of_origin': countries, 'clients': clients}
    print(data)
    return JsonResponse({'status': 'success', 'data': data})
